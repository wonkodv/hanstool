Awesome WM Widget
=================

There is an awesome widget, that can be used as frontend.
To set it up, link the lua module into awesome's seachr path

    ln -s ~/code/hanstool/extra/awesome_wm/ht3.lua ~/.config/awesome/ht3.lua

import the module near the top of awesomes config:

    local ht3 = require "ht3"

and set up a hotkey that opens the prompt

    awful.key({ modkey }, "F8", function () ht3.prompt(awful.screen.focused().mypromptbox.widget) end),

The Members of `ht3.setting` can be overwritten to customize it.


TODO
----

*   shellescape: Currently the input is quoted with `'` and nothing more.
