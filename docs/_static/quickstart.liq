# Showergel's quickstart script for Liquidsoap
# --------------------------------------------
#
# This defines a basic Liquidsoap radio, integrated with Showergel:
#  - Music, recorded shows and jingles are picked from folders
#  - An external stream can be relayed, according to Showergel's schedule
#  - A live stream can connect and takeover the program
#
# Please read the whole script, tune paths and sources/outputs to your needs,
# and start streaming !
#
# ⚠ Always call `liquidsoap --check quickstart.liq` before (re)starting ⚠
#
# Copyright 2022 Martin Kirchgessner
# https://github.com/martinkirch/showergel


############################### BASIC SETTINGS #################################

# URL to your local Showergel installation - this should match your Showergel configuration
SHOWERGEL = "http://localhost:2345"

# Open Liquidsoap's telnet server - this should match values in Showergel configuration at the [liquidsoap] section
settings.server.telnet.set(true)
settings.server.telnet.bind_addr.set("127.0.0.1")
settings.server.telnet.port.set(1234)

# The 3 folders below will be watched by Liquidsoap: to put/remove a file on air,
# just drop/remove it in the folder, or one of its sub-folders.

# Path to your Music folder
MUSIC = "/home/martin/radio/liquidsoap/Music"

# Path to your Jingles folder
JINGLES = "/home/martin/radio/liquidsoap/Jingles"

# Path to pre-recorded shows - we assume there will be a sub-folder per show
SHOWS = "/home/martin/radio/liquidsoap/Shows"


################################# TOOLING #####################################

# This section creates a few operators we'll use afterwards. When starting with
# Liquidsoap you can skip this section and scroll directly to `MUSIC` !


def recorded_show(name)
  show_folder = "#{SHOWS}/#{name}"
  # let's check show_folder exists - if not, the folder is created so the script can start
  if not file.exists(show_folder) then
    log("Created folder #{show_folder}")
    file.mkdir(show_folder)
  end

  # add a 3-hours delay, making this show will be unavailable right after playing
  # this avoids re-playing the show if it's shorter than its allocated time frame.
  delay(id="#{name}_", 10000.,

    # sometimes recorded shows forget a blank in the end - make it at most 10 seconds
    blank.eat(max_blank=10.0, threshold=-50.0,

      # If there's a mono file
      audio_to_stereo(

        # read files from show's folder
        playlist(reload_mode="watch", mode="normal", id=name, show_folder)
      )
    )
  )
end

# auth_function ensures we use Showergel's users directory for their authentication.
def auth_function(login) =
  response = http.post("#{SHOWERGEL}/login",
    headers=[("Content-Type", "application/json")],
    data=json_of(login)
  )
  if response.status_code == 200 then
    log("Access granted to #{login.user}")
    true
  else
    log("Access denied to #{login.user}")
    false
  end
end

# First define a 3s crossfade operator that skips the cutted track.
# Skipping avoids getting back in the middle of a music track after a live show,
# but it requires a weird implementation. See https://github.com/savonet/liquidsoap/issues/1548
def crossfade_3s(a,b)
  faded = add(normalize=false, [
    fade.in(duration=3., type="exp", b),
    amplify(mkfade(duration=3., start=1., stop=0., type="exp", a) ,a)
  ])
  thread.run(delay=10., { source.skip(a) })
  faded
end

############################### END OF TOOLING ##################################


################################### MUSIC ######################################

# When nothing else is playing, thi script will play music. It is the most basic
# auto-DJ, picking random files from the MUSIC folder defined above.
#
# If you want a finer music selection depending on the time of day/day of week,
# we advise you create sources and combine them in a `switch` as recorded shows below.

music = blank.eat(id="music", start_blank=true, max_blank=1.0, threshold=-45.0,
  playlist(MUSIC, id="music_pl", mode="random", reload_mode="watch")
)

############################ RECORDED SHOWS ####################################

# You surely want to edit what follows.

# Each recorded show will have its folder in `SHOWS`, as defined at the
# beginning of this file.

# Now we create per-show sources.
# This example will read files from the /home/radio/Shows/Example/ folder.
example = recorded_show("Example")

# and here comes your programs grid.
# in this example, "Example" is broadcasted on Monday and Saturday mornings.

shows = switch(id="shows", replay_metadata=false, [
  ({1w08h00-1w09h00}, example),
  ({6w08h00-6w09h00}, example),
])

############################### JINGLES ########################################

# This inserts jingles between tracks/shows/streams, at most every 13 minutes.
# On average (and unless you're broadcasting long tracks) this results in a
# "4 IDs per hour" schedule but you can tune the delay to play jingles more
# or less frequently (the greater delay, the less frequent).

jingles = delay(780., id="jingles",
  playlist(JINGLES, id="jingles_pl", mode="random", reload_mode="watch")
)

################################ EXTERNAL RELAY ################################

# We set-up an HTTP source, to maybe relay another stream.
#
# Note that, because of `start=false`, this source will never play unless
# activated by a "external.start" command from Showergel's scheduler (don't
# forget to schedule "external.stop" later) !
# If you want to play the stream as soon as it appears online, remove `start=false,`

external = input.http(id="external", "https://live.campusgrenoble.org/rcg112",
  start=false, max_buffer=30.)


################################ LIVE SHOWS ####################################

# We use Liquidsoap's input.harbor to emulate an Icecast server waiting for
# connections: this allow users to broadcast live shows on our stream.
# Producers should tune their streamer to this machine on the port and mountpoint
# defined below. User and password will be defined via the Showergel interface.

live = input.harbor(
  auth=auth_function,
  buffer=5.,
  max=30.,
  port=9000,
  "live"  # mountpoint name
)

########################### COMBINING SOURCES ##################################

# we add an `ondemand` source so you can play something one by scheduling the command:
# ondemand.push /path/to/file.mp3

q = request.queue(id="ondemand")

########################### COMBINING SOURCES ##################################

# The list given to `fallback` below defines sources' priority: the first available in the list will play.
# The final `blank()` is only here so Liquidsoap will consider `programs` as a safe source.
programs = fallback([live,   external,     q,            shows,        music,        blank()],
  transitions=[crossfade_3s, crossfade_3s, crossfade_3s, crossfade_3s, crossfade_3s],
  track_sensitive=false,
  replay_metadata=false,
  id="programs")

radio = fallback([jingles, programs],
  id="programs_and_jingles",
  replay_metadata=false
)


######################## PLAYOUT LOG TO SHOWERGEL ##############################

# If the SHOWERGEL constant is well defined above, no need to change this
# section - just remove it if you don't want to log metadata to Showergel.

def post_to_showergel(md)
  response = http.post("#{SHOWERGEL}/metadata_log",
    headers=[("Content-Type", "application/json; charset=UTF-8")],
    data=metadata.json.stringify(metadata.cover.remove(md))
  )
  log(label="posted_to_showergel", response.status_message)
end

radio.on_track(fun(m) -> thread.run({post_to_showergel(m)}))


############################ ♫ OUTPUT ♫ ########################################
# Keep/tune your favorite output(s) !

# Output to pulseaudio, which is usually abailable on Linux desktops.
# You can also try `output(radio)` or `output.alsa(radio)` 
output.pulseaudio(radio)

# Stream to Icecast - maybe change values below
# output.icecast(%vorbis, # see https://www.liquidsoap.info/doc-2.0.0/encoding_formats.html
# 	id="icecast",
#       host = "localhost",
#       port = 9000,
#       password = "secretsecret",
#       mount = "radio.ogg",
#       mksafe(buffer(radio))
#     )
