local M = {}

---@class spotify.Config
M.config = {
  -- Whether to show status after an action is executed using the :Spotify command.
  notify_after_action = true,
  defaults = {
    -- The numeric value that represents each -/+ volume increment.
    volume_increment = 5,
    -- The numeric value that represents each -/+ time increment.
    time_increment = 5,
    -- The default action to take when :Spotify shuffle is called.
    shuffle = "toggle",
  },
  notification = {
    -- The notification backend to use. Can be "builtin", "notify", "snacks", or "auto".
    backend = "auto",
    -- Extra options to pass to the vim.notify function.
    extra_opts = {},
    -- The inverval that the notification will be updated (in milliseconds).
    refresh_interval = 100,
    -- How many refresh intervals to cycle through the text that doesn't fit in the notification.
    cycle_speed = 2,
    -- How many refresh intervals to wait before cycling through the text that doesn't fit in the notification.
    initial_cycle_pause = 5,
    -- The timeout for the notification (in milliseconds).
    timeout = 4000,
    -- The width of text in the notification.
    width = 44,
    -- A template to format the notification text.
    -- The template is a list of lists of tables, where each table represents a line of text,
    -- and each line is a list of tables, where each table represents a block of text.
    -- Each block of text can have the following keys:
    --  - content: The text to display.
    --  - width: The width of the block of text, if not specified, the width will be calculated based on the width of the whole line.
    --  - shorten: Whether to truncate the text if it doesn't fit in the block, the text will cycle on each refresh interval.
    --  - align: The alignment of the text in the block, can be "left", "center", or "right".
    --
    --  The content can have the following placeholders:
    --  - {title}: The title of the current track.
    --  - {artists}: The artists of the current track separated by commas.
    --  - {album.name}: The name of the album of the current track.
    --  - {album.artists}: The artists of the album of the current track separated by commas.
    --  - {shuffle.symbol}: The symbol for the shuffle state (as given in the symbols.shuffle table).
    --  - {shuffle.state}: The state of the shuffle (as given in the states.shuffle table).
    --  - {playback.symbol}: The symbol for the playback state (as given in the symbols.playback table).
    --  - {playback.state}: The state of the playback (as given in the states.playback table).
    --  - {volume.symbol}: The symbol for the volume state (as given in the symbols.volume table).
    --  - {volume.state}: The state of the volume (as given in the states.volume table).
    --  - {volume.value}: The value of the volume (from 0 to 100).
    --  - {time.current}: The current time of the track in the format "mm:ss".
    --  - {time.duration}: The duration of the track in the format "mm:ss".
    --  - {progressbar}: A progress bar that represents the current time of the track (as given in the progressbar table).
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
