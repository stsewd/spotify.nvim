local config = require("spotify").config
local notify = require("spotify.notify")

local M = {}

function M.get_actions()
  local actions = {
    ["play/pause"] = { M.play_pause, true },
    play = { M.play, true },
    pause = { M.pause, true },
    stop = { M.stop, true },
    next = { M.next, true },
    prev = { M.prev, true },
    status = { notify.status, true },
    volume = { M.volume, true },
    shuffle = { M.shuffle, true },
    time = { M.time, true },
    show = { M.show, false },
  }
  return actions
end

--- Wrapper around the execution of a spotify command.
---
--- The given arguments are the
--- @param action string name of the action.
--- @param value string value of the action, can be nill.
function M.execute(action, value)
  -- Map of actions to a tuple of functions,
  -- and a boolean, indicating if the status
  -- can be shown after the action has been performed.
  local actions = M.get_actions()
  local item = actions[action]
  -- TODO: maybe return true/false if the operation failed?
  -- This way we can just skip showing the status.
  -- Maybe all commands return the error message as well?
  item[1](value)
  if item[2] and config.show_status_after_action then
    notify.status()
  end
end

function M.play_pause()
  vim.fn.SpotifyAction("play/pause")
end

function M.play()
  vim.fn.SpotifyAction("play")
end

function M.pause()
  vim.fn.SpotifyAction("pause")
end

function M.stop()
  vim.fn.SpotifyAction("stop")
end

function M.next()
  vim.fn.SpotifyAction("next")
end

function M.prev()
  vim.fn.SpotifyAction("prev")
end

function M.show()
  vim.fn.SpotifyAction("show")
end

function M.volume(value)
  if value == nil then
    value = "+10"
  end
  return vim.fn.SpotifyAction("volume", value)
end

function M.shuffle(value)
  if value == nil then
    value = "toggle"
  end
  vim.fn.SpotifyAction("shuffle", value)
end

function M.time(value)
  if value == nil then
    value = "+10"
  end
  vim.fn.SpotifyAction("time", value)
end

return M
