local M = {}

M.config = {
  refresh_interval = 50,
  cycle_speed = 5,
  show_status_after_action = true,
  timeout = 3000,
  render = {
    -- template
    -- symbols
    -- progress_bar_width
    -- width
  },
}

local function completion(arglead, cmdline, cursorpos)
  local actions = require("spotify.actions")
  return vim.tbl_keys(actions.get_actions())
end

function M.setup(opts)
  -- Merge config with defaults
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})

  -- Create command.
  vim.api.nvim_create_user_command("Spotify", function(cmd_opts)
    local actions = require("spotify.actions")
    actions.execute(cmd_opts.fargs[1], cmd_opts.fargs[2])
  end, { nargs = "+", complete = completion })
end

return M
