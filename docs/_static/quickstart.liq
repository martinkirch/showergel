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
# Copyright 2021-2022 Martin Kirchgessner
# https://github.com/martinkirch/showergel



# anything after a # will be ignored by Liquidsoap



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
MUSIC = "/home/radio/Music"

# Path to your Jingles folder
JINGLES = "/home/radio/Jingles"

# Path to pre-recorded shows - we assume there will be a sub-folder per show
SHOWS = "/home/radio/Shows"


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

# auth_function ensures incoming streams are authenticated against Showergel's users directory
def auth_function(login) =
  response = http.post("#{SHOWERGEL}/login",
    headers=[("Content-Type", "application/json")],
    data=json.stringify(login)
  )
  if response.status_code == 200 then
    log("Access granted to #{login.user}")
    true
  else
    log("Access denied to #{login.user}")
    false
  end
end

# a 3-seconds crossfade operator that skips the cutted track.
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

# When nothing else is playing, thi script will play music. We use the most basic
# auto-DJ, picking random files from the MUSIC folder defined above.
#
# If you want a finer music selection depending on the time of day/day of week,
# we advise you create additional sources and combine them in a `switch` as
# recorded shows below.

music = blank.eat(id="music", start_blank=true, max_blank=1.0, threshold=-45.0,
  playlist(MUSIC, id="music_pl", mode="random", reload_mode="watch")
)

############################ RECORDED SHOWS ####################################

# You surely want to edit what follows.

# Each recorded show will have its folder in `SHOWS`, as defined at the
# beginning of this file.

# We create on source per recorded show - define one per line, give them
# different names, without spaces.
# This example will read files from the /home/radio/Shows/Example/ folder.
example = recorded_show("Example")

# Then we implement the programs grid with time conditions in a `switch` operator.
# in this example, "Example" is broadcasted on Monday and Saturday mornings.
# The time interval on the left only defines when the program can start - if one
# file is longer than the given interval it will not be stopped.
# Add `track_sensitive=false` to the `switch` arguments if you prefer cutting.

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
# activated by a "external.start" command from Showergel's scheduler. Don't
# forget to schedule "external.stop" later.
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

########################### FILE REQUESTS QUEUE ################################

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

########################### OPTIONAL : NORMALIZATION ##################################

# remove the # at the beginning of next line to enable normalization

# radio = normalize(target=-13., lufs=true, gain_max=12., gain_min=-12., down=0.1, up=1., window=1., radio)

# This is one of the many ways to normalize with liquidsoap
# see https://www.liquidsoap.info/doc-dev/reference.html#normalize
# you may apply it to only on source : live, show(s), jingles...
# Or tag tracks with replay gain information.

######################## PLAYOUT LOG TO SHOWERGEL ##############################

# If the SHOWERGEL constant is well defined above, no need to change this
# section - just remove it if you don't want to log metadata to Showergel.

def post_to_showergel(md)
  response = http.post("#{SHOWERGEL}/metadata_log",
    headers=[("Content-Type", "application/json; charset=UTF-8")],
    data=metadata.json.stringify(metadata.cover.remove(md))
  )
  if response.status_code != 200
  then
    log(label="Warning", "Error while posting metadata to Showergel: #{response} #{response.status_code} #{response.status_message}")
  end
end

radio.on_metadata(fun(m) -> thread.run(fast=false, {post_to_showergel(m)}))


############################ ♫ OUTPUT ♫ ########################################
# Add/remove/tune your favorite outputs !

# Output to the first available sound card
output(radio)
# On Linux you can also try `output.pulseaudio(radio)` or `output.alsa(radio)` 

# Uncomment below to stream to Icecast
# output.icecast(%vorbis, # see https://www.liquidsoap.info/doc-2.0.0/encoding_formats.html
# 	id="icecast",
#   host = "localhost",
#   port = 9000,
#   password = "secretsecret",
#   mount = "radio.ogg",
#   radio
# )
