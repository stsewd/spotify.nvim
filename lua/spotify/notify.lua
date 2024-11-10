local config = require("spotify").config

local M = {}

-- Local variable to keep track of the current open notification and timer.
local notification_id = nil
local current_cycle = 0
local timeout = 0
local timer = nil

local function close_timer()
  if timer == nil then
    return
  end
  pcall(timer.stop, timer)
  pcall(timer.close, timer)
  timer = nil
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
  current_cycle = 0
  -- One notification per timer.
  notification_id = nil

  -- -- Use a different notification id for each timer.
  -- if using_snacks then
  --   notification_id = "spotify-status-" .. vim.uv.now()
  -- end

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
        end
      end
      local status = vim.fn.SpotifyRenderStatus(math.floor(current_cycle / config.cycle_speed), config.render)
      if not status or status == vim.NIL then
        close_timer()
        return
      end

      local resp = vim.notify(status, vim.log.levels.INFO, opts)
      if using_notify then
        notification_id = resp
      end

      current_cycle = current_cycle + 1
      timeout = timeout - config.refresh_interval
    end)
  )
end

return M
