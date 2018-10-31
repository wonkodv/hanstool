local ht3 = {}

local awful = require "awful"
local naughty = require "naughty"

ht3.settings = {
    complete_exe    = "python -m ht3client -c",
    run_exe         = "python -m ht3client",
    prompt          = "<b>HT:</b> ",
    history_path    = awful.util.getdir("cache") .. "/history_ht3",
    result_callback = function(command, textbox)
        return function (line)
            naughty.notify {
                text    = line,
                title   = command,
                timeout = 3,
            }
            -- textbox.text = "HT => "..line.." < "
        end
    end,
    error_callback  = function(command, textbox)
        return function (line)
            naughty.notify {
                text    = line,
                title   = command,
                timeout = 15,
                fg      = "red",
            }
        end
    end,
}

function ht3.shellescape(s)
    return "'"..s.."'" -- TODO
end

function ht3.prompt(textbox)
    local cache = {}
    local cached_text  = nil
    local fh    = nil
    local complete = function (text, pos, no)
        -- If the text to complete changed, open new completion process handle
        -- If the completion index is not cached, try to read a new line
        -- If the completion index is still not cached, cycle back to uncompleted
        if cached_text ~= text then
            if fh then
                fh:close()
            end
            cached_text = text
            cache= {}
            fh = io.popen(ht3.settings.complete_exe.." "..ht3.shellescape(text))
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
        local r = cache[no]
        return r, #r+1
    end

    awful.prompt.run {
        textbox = textbox,
        prompt  = ht3.settings.prompt,
        exe_callback = function (command)
            awful.spawn.with_line_callback(ht3.settings.run_exe .." ".. ht3.shellescape(command), {
                stdout = ht3.settings.result_callback(command, textbox),
                stderr = ht3.settings.error_callback(command, textbox),
            })
        end,
        history_path = ht3.settings.history_path,
        completion_callback = complete
    }
end


return ht3
