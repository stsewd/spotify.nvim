local M = {}

---@class spotify.Config
M.config = {
  show_status_after_action = true,
  defaults = {
    volume_increment = 5,
    time_increment = 5,
    shuffle = "toggle",
  },
  notification = {
    backend = "auto",
    extra_opts = {},
    refresh_interval = 50,
    cycle_speed = 5,
    initial_cycle_pause = 6,
    timeout = 4000,
    width = 44,
    template = {
      {
        {
          content = "🎶",
          width = 2,
        },
        {
          content = "{title}",
          shorten = true,
        },
      },
      {
        {
          content = "👥",
          width = 2,
        },
        {
          content = "{artists}",
          shorten = true,
        },
      },
      {
        {
          content = "💿",
          width = 2,
        },
        {
          content = "{album.name}",
          shorten = true,
        },
      },
      {},
      {
        {
          content = "",
          width = 5,
        },
        {
          content = "{shuffle.symbol} {shuffle.state}",
          align = "left",
        },
        {
          content = "{playback.symbol}",
          align = "center",
        },
        {
          content = "{volume.symbol} {volume.value}%",
          align = "right",
        },
        {
          content = "",
          width = 5,
        },
      },
      {},
      {
        {
          content = "{time.current} / {time.duration}",
          align = "center",
        },
      },
      {
        {
          content = "{progressbar}",
          align = "center",
        },
      },
    },
    symbols = {
      playback = {
        playing = "▶",
        paused = "⏸",
        stopped = "■",
      },
      shuffle = {
        enabled = "🔀",
        -- disabled = "🔁",
        disabled = "⤭",
      },
      volume = {
        muted = "🔇",
        low = "🔈",
        medium = "🔉",
        high = "🔊",
      },
    },
    states = {
      playback = {
        playing = "playing",
        paused = "paused",
        stopped = "stopped",
      },
      shuffle = {
        enabled = "on",
        disabled = "off",
      },
      volume = {
        muted = "muted",
        low = "low",
        medium = "medium",
        high = "high",
      },
    },
    progressbar = {
      marker = "●",
      filled = "─",
      remaining = "┈",
      width = 40,
    },
  },
}

local function detect_notification_backend()
  local ok, result = pcall(require, "notify")
  if ok and result == vim.notify then
    return "notify"
  end
  ok, result = pcall(require, "snacks")
  if ok and result.config.notifier.enabled then
    return "snacks"
  end
  return "builtin"
end

local function completion(arglead, cmdline, cursorpos)
  local actions = require("spotify.actions")
  return vim.tbl_keys(actions.get_actions())
end

---@param opts spotify.Config?
function M.setup(opts)
  -- Merge config with defaults
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})

  if M.config.notification.backend == "auto" then
    M.config.notification.backend = detect_notification_backend()
  end

  -- Create command.
  vim.api.nvim_create_user_command("Spotify", function(cmd_opts)
    local actions = require("spotify.actions")
    actions.execute(cmd_opts.fargs[1], cmd_opts.fargs[2])
  end, { nargs = "+", complete = completion, force = true })
end

return M
