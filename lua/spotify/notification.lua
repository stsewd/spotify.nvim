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

function M.show()
  -- If called again, just reset the timer.
  timeout = config.notification.timeout

  local using_snacks = config.notification.backend == "snacks"
  local using_notify = config.notification.backend == "notify"

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

  -- Use a different notification id for each timer.
  if using_snacks then
    notification_id = "spotify-status-" .. vim.uv.now()
  end

  timer = vim.uv.new_timer()
  timer:start(
    -- Start the timer immediately.
    0,
    -- Repeat after refresh_interval (milliseconds)
    config.notification.refresh_interval,
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
        opts.id = notification_id
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
      local cycle = math.floor(current_cycle / config.notification.cycle_speed)
      -- This takes some time to run, and makes the timer not accurate.
      local ok, status = unpack(vim.fn.SpotifyRenderStatus(cycle, config.notification))
      if not ok then
        close_timer()
        vim.notify(status, vim.log.levels.ERROR, opts)
        return
      end

      -- Merge opts with user provided opts.
      opts = vim.tbl_extend("force", opts, config.notification.extra_opts)
      local resp = vim.notify(status, vim.log.levels.INFO, opts)
      if using_notify then
        notification_id = resp
      end

      current_cycle = current_cycle + 1
      timeout = timeout - config.notification.refresh_interval
    end)
  )
end

return M
