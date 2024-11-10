local config = require("spotify.config")

local M = {}

local function completion(arglead, cmdline, cursorpos)
  local actions = require("spotify.actions")
  return vim.tbl_keys(actions.get_actions())
end

function M.setup(opts)
  -- Merge config with defaults
  config = vim.tbl_deep_extend("force", config, opts or {}) or {}

  -- Create command.
  vim.api.nvim_create_user_command("Spotify", function(cmd_opts)
    local actions = require("spotify.actions")
    actions.execute(cmd_opts.fargs[1], cmd_opts.fargs[2])
  end, { nargs = "+", complete = completion })
end

return M
