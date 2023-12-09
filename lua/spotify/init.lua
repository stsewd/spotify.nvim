local M = {}

local config = {
  refresh_interval = 50,
  cycle_speed = 5,
  show_status_after_action = true,
  -- wait_time?
  timeout = nil,
  render = {
    -- return_array=false
    -- template
    -- symbols
    -- progress_bar_width
    -- width
  }
}

local function completion (arglead, cmdline, cursorpos)
  local result = {"play", "pause", "play/pause"}
  -- local i = 1
  -- for action in ipairs(get_actions())
  --   result[i] = action
  -- end
  return result
end

-- Local variable to keep track of the current open notification.
local open_notification = nil

function M.setup(opts)
  -- Merge config with defaults
  config = vim.tbl_deep_extend("force", config, opts or {}) or {}

  -- Create command.
  vim.api.nvim_create_user_command("Spotify", function(cmd_opts)
    M._execute(cmd_opts.fargs[1], cmd_opts.fargs[2])
  end, { nargs = '+', complete = completion })
end

local function get_actions ()
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

function M.status()
  local current_cycle = 0
  local status = vim.fn.SpotifyRenderStatus(current_cycle, config.render)
  if status == vim.NIL then
    -- There is a bug in pynvim, run the command again.
    -- Or there was an error when connecting to Spotify.
    return
  end
  local opts = {
    title = "Spotify",
    on_close = function()
      -- Reset the value when the notification window is closed.
      open_notification = nil
    end,
    on_open = function()
      local timer = vim.loop.new_timer()
      local on_close = function()
        pcall(timer.stop, timer)
        pcall(timer.close, timer)
        open_notification = nil
      end
      --
      timer:start(
        -- Start the timer after refresh_interval (milliseconds)
        config.refresh_interval,
        -- Repeat after refresh_interval (milliseconds)
        config.refresh_interval,
        -- Callback
        vim.schedule_wrap(function()
          current_cycle = current_cycle + 1
          -- TODO: see if we can calculate the cylce speed from the refresh_interval.
          local status_ = vim.fn.SpotifyRenderStatus(math.floor(current_cycle / config.cycle_speed), config.render)
          -- If the call failed or if there isn't an open notification, stop the timer.
          if status_ == vim.NIL or not open_notification then
            on_close()
            return
          end
          -- TODO: why do we have a timeout?
          local timeout = config.timeout or 0
          timeout = timeout - config.refresh_interval * current_cycle
          if timeout <= 0 then
            on_close()
            return
          end
          local opts_ = {
            title = "Spotify",
            on_close = on_close,
            hide_from_history = true,
            -- If there is an open window already, just use that.
            replace = open_notification,
            -- TODO: Override the global timeout? Why?
            -- To avoid an infinite loop? Probably.
            timeout = timeout,
          }
          -- Replace the current notification till the timeout has been completed,
          -- but we should find a way to reset the timeout once the user triggers
          -- a new notification.
          open_notification = vim.notify(status_, vim.log.levels.INFO, opts_)
        end)
      )
    end,
  }

  -- Set the initial timeout,
  -- or use the default from the notification.
  if config.timeout then
    opts.timeout = config.timeout
  end

  -- Avoid opening a new notification
  -- if there is one already open.
  if open_notification then
    opts.hide_from_history = true
    opts.replace = open_notification
  end
  open_notification = vim.notify(status, vim.log.levels.INFO, opts)
end

return M
