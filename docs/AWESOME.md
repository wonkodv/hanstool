Awesome WM Widget
=================

To send commands to the `ht3.htd`, you can put something like the 
following into your `rc.lua`. Press `Mod4 + F8` type a command string
and hit Enter.

    awful.key({ modkey }, "F8",
              function ()
                  awful.prompt.run(
				  	{ prompt = "HT: " },
					mypromptbox[mouse.screen].widget,
					function (s) 
						awful.util.spawn( "python3 -m ht3.client '" .. s .."'")
					end,
					nil,
					awful.util.getdir("cache") .. "/history_ht3")
              end),

TODO
----

*   shellescape
*   completion
