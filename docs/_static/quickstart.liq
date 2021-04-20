# Showergel's quickstart script for Liquidsoap
# --------------------------------------------
#
# This is intended both as a Showergel integration demo and as a radio:
# bootstrapper: it sets basic sources (music, show, jingle, external, live) and
# outputs to the first sound card available. Read the whole script, tune paths
# and sources/outputs to your needs, a start streaming !
#
# Always call `liquidsoap --check quickstart.liq` before (re)starting !
#
# Copyright 2021 Martin Kirchgessner
# https://github.com/martinkirch/showergel


# URL to your local Showergel installation - this also depends on tour Showergel configuration
SHOWERGEL = "http://localhost:2345"

# Open Liquidsoap's telnet server - this should match values in Showergel configuration at the [liquidsoap] section
set("server.telnet",true)
set("server.telnet.bind_addr","127.0.0.1")
set("server.telnet.port",1234)

# The 3 folders below will be watched by Liquidsoap: to put/remove a file on air,
# just drop/remove it in the folder (or one of its sub-folders).

# Path to your Music folder
MUSIC = "/home/martin/Music"

# Path to your Jingles folder
JINGLES = "/home/martin/Jingles"

# Path to pre-recorded shows - we assume there will be a sub-folder per show
SHOWS = "/home/martin/Shows"

# Note that the list given to `fallback`s below defines the sources' priority:
# the first available in the list will play.


################################# MUSIC ######################################

# this is the most basic auto-DJ: pick random files from our MUSIC folder
#
# if you want to vary music selection depending on the time of day/day of week,
# we advise you create sources and combine them in a switch as recorded shows below.

music = eat_blank(id="music", start_blank=true, max_blank=1.0, threshold=-45.0,
  playlist(MUSIC, id="music_pl", mode="random", reload_mode="watch")
)

############################ RECORDED SHOWS ####################################

def show_source(name)
  # add a 3-hours delay, making this show will be unavailable right after playing
  # this avoids re-playing the show if it's shorter than its allocated time frame.
  delay(id="#{name}_", 10000.,

    # sometimes recorded shows forget a blank in the end - make it at most 10 seconds
    eat_blank(max_blank=10.0, threshold=-50.0,

      # If there's a mono file
      audio_to_stereo(

        # read files from show's folder
        playlist(reload_mode="watch", mode="normal", id=name, "#{SHOWS}/#{name}")
      )
    )
  )
end

# Now we create per-show sources.
# This example will read files from the /home/martin/Shows/Morning/ folder.
morning = show_source("Morning")

# and here comes your programs grid.
# in this example, "Morning" is broadcasted on Monday and Saturday mornings.

shows = switch(id="shows", replay_metadata=false, [
  ({1w08h00-1w09h00}, morning),
  ({6w08h00-6w09h00}, morning),
])


################################ EXTERNAL RELAY ################################

# We set-up an HTTP source, if we ever want to relay another stream.
#
# If the stream comes from an HTTPS server, use `input.https` instead.
#
# Note that, because of `autostart=false`, this source will never play unless
# activated by a "external.start" command from Showergel's scheduler (don't
# forget to schedule "external.stop" later) !
# If you want to play the stream as soon as it appears online, just remove `autostart=false`

external = input.http(id="external", "http://live.campusgrenoble.org:9000/rcg112",
  autostart=false, buffer=3., max=30.)


################################ LIVE SHOWS ####################################

# We use Liquidsoap's input.harbor to emulate an Icecast server waiting for
# connections: this allow users to broadcast live shows on our stream.
# Producers should tune their streamer to this machine on the port and mountpoint
# defined below.

# auth_function ensures we use Showergel's users directory for their authentication.

def auth_function(user, password) =
  let (status, _, _) = http.post("#{SHOWERGEL}/login",
    headers=[("Content-Type", "application/json")],
    data=json_of([("username", user), ("password", password)])
  )
  let (_, code, _) = status
  if code == 200 then
    log("Access granted to #{user}")
    true
  else
    log("Access denied to #{user}")
    false
  end
end

live = input.harbor(
  auth=auth_function,
  buffer=5.,
  max=30.,
  port=9000,
  "live"  # mountpoint name
)


########################### COMBINING SOURCES ##################################

# First define a 3s crossfade that will skip the cutted track.
# Skipping avoids getting back in the middle of a music track after a live show,
# but it requires a weird implementation. See https://github.com/savonet/liquidsoap/issues/1548
def crossfade_3s(a,b)
  faded = add(normalize=false, [
    fade.in(duration=3., type="exp", b),
    amplify(mkfade(duration=3., start=1., stop=0., type="exp", a) ,a)
  ])
  add_timeout(10., { source.skip(a) ; -1.})
  faded
end

# The final `blank()` is here so Liquidsoap will consider `programs` as a safe source,
# although in practice it will only play if `music` is empty, which is very unlikely.
programs = fallback([live,   external,     shows,       music,        blank()],
  transitions=[crossfade_3s, crossfade_3s, crossfade_3s, crossfade_3s],
  track_sensitive=false,
  replay_metadata=false,
  id="programs")


############################### JINGLES ########################################

# This inserts jingles between tracks boundaries, at most each 13 minutes.
# On average (and unless you're broadcasting long tracks) this results in a
# traditional "4 IDs per hour" schedule.

jingles = delay(780., id="jingles",
  playlist(JINGLES, id="jingles_pl", mode="random", reload_mode="watch"),
)

programs_and_jingles = fallback([jingles, programs],
  id="programs_and_jingles",
  replay_metadata=false
)


##################### LOG TRACKS TO SHOWERGEL ##################################

def post_to_showergel(m)
    response = http.post("#{SHOWERGEL}/metadata_log",
        headers=[("Content-Type", "application/json")],
        data=json_of(m))
    log(label="posted_to_showergel", string_of(response))
end

radio = on_track(post_to_showergel, programs_and_jingles)


############################ ♫ OUTPUT ♫ ########################################

output.prefered(radio)
