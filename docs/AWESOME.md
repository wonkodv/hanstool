Awesome WM Widget
=================

To send commands to the `ht3.htd`, you can put something like the 
following into your `rc.lua`. Press `Mod4 + F8` type a command string
and hit Enter.

    awful.key({ modkey }, "F8",
            function ()
                awful.prompt.run {
                    prompt  = "<b>HT:</b> ",
                    textbox = awful.screen.focused().mypromptbox.widget,
                    exe_callback = function (s)
                        awful.util.spawn( "python3 -m ht3.client '" .. s .."'")
                    end,
                    history_path = awful.util.getdir("cache") .. "/history_ht3",
                    completion_callback = function (text, pos, no)
                        return text.." TODO", pos+5
                    end,
                }
            end),

TODO
----

*   shellescape
*   completion
