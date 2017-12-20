Awesome WM Widget
=================

To send commands to the `ht3.htd`, you can put something like the 
following into your `rc.lua`. Press `Mod4 + F8` type a command string
and hit Enter. Completion is also obtained from htd.

    awful.key({ modkey }, "F8",
            function ()
                local cache = {}
                local cached_text  = nil
                local fh    = nil
                local complete = function (text, pos, no)
                    -- If the text to complete changed, open new completion process handle
                    -- If the completion index is not cached, try to read a new line
                    -- If the completion index is still not cached, cycle back to uncompleted
                    if cached_text ~= text then
                        print("recomplete: "..text)
                        if fh then
                            fh:close()
                        end
                        cached_text = text
                        cache= {}
                        fh = io.popen("python -m ht3.client -c '"..text.."'")
                    end
                    if fh and #cache < no then
                        line = fh:read()
                        cache[no] = line
                        if line == nil then
                            fh = nil
                        end
                    end
                    if #cache < no then
                        no = no % (#cache + 1)
                    end
                    if no == 0 then
                        return text, #text+1
                    end
                    r = cache[no]
                    return r, #r+1
                end

                awful.prompt.run {
                    prompt  = "<b>HT:</b> ",
                    textbox = awful.screen.focused().mypromptbox.widget,
                    exe_callback = function (s)
                        awful.util.spawn( "python3 -m ht3.client '" .. s .."'")
                    end,
                    history_path = awful.util.getdir("cache") .. "/history_ht3",
                    completion_callback = complete
                }
            end),

TODO
----

*   shellescape
