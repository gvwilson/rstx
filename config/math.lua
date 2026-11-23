-- math.lua
-- Inject KaTeX when the project opts in with `mccole-math: true` in
-- _quarto.yml. The minimal HTML template does not load a math renderer,
-- so this filter supplies KaTeX and renders every <span class="math">.

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local content = f:read("*a")
  f:close()
  return content
end

local KATEX = [[
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {
  var elems = document.getElementsByClassName("math");
  for (var i = 0; i < elems.length; i++) {
    var el = elems[i];
    var tex = el.firstChild;
    if (el.tagName === "SPAN" && tex) {
      katex.render(tex.data, el, {
        displayMode: el.classList.contains("display"),
        throwOnError: false
      });
    }
  }
});
</script>
]]

function Pandoc(doc)
  local project_dir = quarto.project.directory or "."
  local yaml = read_file(project_dir .. "/_quarto.yml") or ""
  if yaml:match("mccole%-math:%s*true") then
    doc.meta["header-includes"] = pandoc.MetaBlocks({
      pandoc.RawBlock("html", KATEX),
    })
  end
  return doc
end
