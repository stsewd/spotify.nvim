local M = {}

local config = {
  refresh_interval = 50,
  cycle_speed = 5,
  show_status_after_action = true,
  timeout = 3000,
  render = {
    -- return_array=false
    -- template
    -- symbols
    -- progress_bar_width
    -- width
  },
}

local function completion(arglead, cmdline, cursorpos)
  local result = { "play", "pause", "play/pause" }
  -- local i = 1
  -- for action in ipairs(get_actions())
  --   result[i] = action
  -- end
  return result
end

-- Local variable to keep track of the current open notification.
local notification_id = nil
local current_cycle = 0
local timeout = 0
local timer = nil

function M.setup(opts)
  -- Merge config with defaults
  config = vim.tbl_deep_extend("force", config, opts or {}) or {}

  -- Create command.
  vim.api.nvim_create_user_command("Spotify", function(cmd_opts)
    M._execute(cmd_opts.fargs[1], cmd_opts.fargs[2])
  end, { nargs = "+", complete = completion })
end

local function get_actions()
  local actions = {
    ["play/pause"] = { M.play_pause, true },
    play = { M.play, true },
    pause = { M.pause, true },
    stop = { M.stop, true },
    next = { M.next, true },
    prev = { M.prev, true },
    status = { M.status, true },
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
function M._execute(action, value)
  -- Map of actions to a tuple of functions,
  -- and a boolean, indicating if the status
  -- can be shown after the action has been performed.
  local actions = get_actions()
  local item = actions[action]
  -- TODO: maybe return true/false if the operation failed?
  -- This way we can just skip showing the status.
  -- Maybe all commands return the error message as well?
  item[1](value)
  if item[2] and config.show_status_after_action then
    -- Wait here?
    M.status()
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
  return vim.fn.SpotifyAction("volume", value)
end

function M.shuffle(value)
  vim.fn.SpotifyAction("shuffle", value)
end

function M.time(value)
  vim.fn.SpotifyAction("time", value)
end

local function close_timer()
  if timer == nil then
    return
  end
  pcall(timer.stop, timer)
  pcall(timer.close, timer)
  timer = nil
end

local function reset()
  current_cycle = 0
  notification_id = nil
end

function M.status()
  -- If called again, just reset the timer.
  timeout = config.timeout
  -- TODO: these should be configurable,
  -- or maybe autodetect if the user has the plugins installed.
  -- for now, make it work for both, since they don't conflict (yet).
  local using_snacks = true
  local using_notify = true

  -- If there is a timer running, just return,
  -- since the timeout was reset.
  if timer ~= nil and timer:get_due_in() > 0 then
    return
  end

  -- Just in case?
  close_timer()

  -- Restart the cycle only if the timer is not running.
  -- So the user can keep seeing the current status.
  reset()

  timer = vim.uv.new_timer()
  timer:start(
    -- Start the timer immediately.
    0,
    -- Repeat after refresh_interval (milliseconds)
    config.refresh_interval,
    -- Callback
    vim.schedule_wrap(function()
      if timeout <= 0 then
        close_timer()
        reset()
        return
      end

      local opts = {
        title = "Spotify",
        timeout = timeout,
      }

      if using_snacks then
        opts.id = "spotify-status"
        opts.ft = "spotify-status"
      end

      if using_notify then
        if notification_id ~= nil then
          opts.replace = notification_id
          opts.hide_from_history = true
        end
        opts.on_close = function()
          close_timer()
          reset()
        end
      end
      local status = vim.fn.SpotifyRenderStatus(math.floor(current_cycle / config.cycle_speed), config.render)
      notification_id = vim.notify(status, vim.log.levels.INFO, opts)
      current_cycle = current_cycle + 1
      timeout = timeout - config.refresh_interval
    end)
  )
end

return M
