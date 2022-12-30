local M = {}
local config = {}
local open_notification = nil

function M.setup(opts)
  config = vim.tbl_deep_extend("force", config, opts or {}) or {}
end

function M.play_pause()
  vim.fn.SpotifyAction('play/pause')
end

function M.play()
  vim.fn.SpotifyAction('play')
end

function M.pause()
  vim.fn.SpotifyAction('pause')
end

function M.stop()
  vim.fn.SpotifyAction('stop')
end

function M.next()
  vim.fn.SpotifyAction('next')
end

function M.prev()
  vim.fn.SpotifyAction('prev')
end

function M.show()
  vim.fn.SpotifyAction('show')
end

function M.volume(value)
  return vim.fn.SpotifyAction('volume', value)
end

function M.shuffle(value)
  vim.fn.SpotifyAction('shuffle', value)
end

function M.time(value)
  vim.fn.SpotifyAction('time', value)
end

function M.status()
  local current_cycle = 0
  local status = vim.fn.SpotifyRenderStatus(true, current_cycle)
  if status ~= vim.NIL then
    local opts = {
      title = "Spotify",
      on_close= function ()
        open_notification = nil
      end,
    }
    opts.on_open = function ()
      local timer = vim.loop.new_timer()
      timer:start(50, 50, vim.schedule_wrap(function()
        current_cycle = current_cycle + 1
        local status_ = vim.fn.SpotifyRenderStatus(true, math.floor(current_cycle / 5))
        if status_ == vim.NIL or not open_notification then
          return
        end
        local opts_ = {
          title = "Spotify",
          on_close= function ()
            pcall(timer.close, timer)
            open_notification = nil
          end,
          hide_from_history = true,
          replace=open_notification,
          timeout=0,
        }
        open_notification = vim.notify(status_, vim.log.levels.INFO, opts_)
      end))
    end

    if open_notification then
      opts.hide_from_history = true
      opts.replace = open_notification
    end
    open_notification = vim.notify(status, vim.log.levels.INFO, opts)
  end
end

return M
