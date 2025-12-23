#!/usr/bin/env ruby

require 'fileutils'
require 'optparse'
require 'io/console'

def get_system_python
  output = `python3 --version 2>&1`
  match = output.match(/Python (\d+\.\d+)/)
  return match ? match[1] : "3.12"
end

class UI
  CYAN = "\e[36m"
  GREEN = "\e[32m"
  DIM = "\e[2m"
  RESET = "\e[0m"
  CLEAR_LINE = "\e[2K\r"

  def self.ask(question, default: nil)
    print "#{GREEN}◇#{RESET}  #{question} "
    print "#{DIM}(#{default})#{RESET} " if default
    print "\n#{DIM}│#{RESET}  "
    input = gets.chomp
    print "\e[1A#{CLEAR_LINE}"
    result = input.empty? ? default : input
    puts "#{GREEN}✔#{RESET}  #{question} #{CYAN}#{result}#{RESET}"
    result
  end

  def self.select(question, options)
    print "#{GREEN}◇#{RESET}  #{question}\n"
    cursor = 0
    loop do
      options.each_with_index do |opt, i|
        prefix = (i == cursor) ? "#{CYAN}❯#{RESET}" : " "
        label = (i == cursor) ? "#{CYAN}#{opt}#{RESET}" : opt
        print "#{DIM}│#{RESET}  #{prefix} #{label}\n"
      end
      case read_char
      when "\e[A" then cursor = (cursor - 1) % options.length
      when "\e[B" then cursor = (cursor + 1) % options.length
      when "\r", "\n"
        print "\e[#{options.length}A\e[J"
        puts "#{GREEN}✔#{RESET}  #{question} #{CYAN}#{options[cursor]}#{RESET}"
        return options[cursor]
      when "\u0003" then exit 1
      end
      print "\e[#{options.length}A"
    end
  end

  def self.confirm(question)
    print "#{GREEN}◆#{RESET}  #{question} (y/N) "
    input = gets.chomp.downcase
    input == 'y'
  end

  def self.read_char
    STDIN.echo = false; STDIN.raw!
    input = STDIN.getc.chr
    if input == "\e" then
      input << STDIN.read_nonblock(3) rescue nil
      input << STDIN.read_nonblock(2) rescue nil
    end
  ensure
    STDIN.echo = true; STDIN.cooked!
    return input
  end
end

def generate_toml(name, linter, type_checker, use_scripts, py_ver)
  config = ""
  ruff_ver = "py#{py_ver.delete('.')}"

  if linter.include?("Ruff")
    config += <<~TOML
      [tool.ruff]
      line-length = 88
      target-version = "#{ruff_ver}"
      
      [tool.ruff.lint]
      select = ["E", "F", "I", "N", "UP", "B"]
      fixable = ["ALL"]
      
      [tool.ruff.format]
      quote-style = "double"
    TOML
  end

  if type_checker.include?("Ty")
    config += <<~TOML

      [tool.ty]
      # Ty defaults
    TOML
  elsif type_checker.include?("Mypy")
    config += <<~TOML

      [tool.mypy]
      strict = true
      ignore_missing_imports = true
      disallow_untyped_defs = true
    TOML
  end

  if use_scripts
    check_cmd = "ty check" if type_checker.include?("Ty")
    check_cmd = "mypy ."   if type_checker.include?("Mypy")

    lint_cmd = "ruff check . --fix" if linter.include?("Ruff")

    chain_cmd = "#{lint_cmd} && #{check_cmd} && python main.py"

    config += <<~TOML

      [tool.poe.tasks]
      start = "python main.py"
      lint  = "#{lint_cmd}"
      check = "#{check_cmd}"
      check-all = { shell = "#{chain_cmd}", help = "Lint, check types, and run app" }
      dev = "watchfiles 'uv run poe check-all' ."
    TOML
  end

  <<~TOML
    [project]
    name = "#{name}"
    version = "0.1.0"
    description = "Project generated with create-py-app"
    readme = "README.md"
    requires-python = ">=#{py_ver}"
    dependencies = []

    #{config}
  TOML
end

def generate_main_py(name)
  <<~PYTHON
    def main() -> None:
        print("Hello from #{name}!")
        print("Run 'uv run poe dev' to start hot-reloading.")

    if __name__ == "__main__":
        main()
  PYTHON
end

options = { git: true }
ARGV.options { |opts| opts.on("--no-git") { options[:git] = false } }.parse!

detected_ver = get_system_python
puts "#{UI::DIM}Detected System Python: #{detected_ver}#{UI::RESET}"

project_name = ARGV[0] || UI.ask("Project name:", default: "my-py-app")

if Dir.exist?(project_name)
  puts "\n\e[31mDirectory '#{project_name}' already exists.\e[0m"
  exit 1
end

framework = UI.select("Select a framework:", ["Vanilla"])
linter_choice = UI.select("Select a linter:", ["Ruff (Fast, Recommended)", "None"])
type_choice = UI.select("Select a type checker:", ["Ty (Astral - Fast)", "Mypy (Standard)", "None"])

scripts_choice = UI.confirm("Add dev scripts (hot-reloading)?")
should_install = UI.confirm("Install dependencies now?")

puts "\nCreating project in \e[36m#{project_name}\e[0m..."

Dir.mkdir(project_name)
Dir.chdir(project_name) do
  system("uv init --python #{detected_ver} --quiet")

  File.write("main.py", generate_main_py(project_name))

  deps = []
  deps << "ruff" if linter_choice.include?("Ruff")
  deps << "ty"   if type_choice.include?("Ty")
  deps << "mypy" if type_choice.include?("Mypy")
  
  if scripts_choice
    deps << "poethepoet"
    deps << "watchfiles"
  end

  File.write("pyproject.toml", generate_toml(project_name, linter_choice, type_choice, scripts_choice, detected_ver))

  if should_install
    if deps.any?
      puts "    Installing: #{deps.join(', ')}..."
      system("uv add --dev #{deps.join(' ')} --quiet")
    else
      system("uv sync --quiet")
    end

    if linter_choice.include?("Ruff")
      puts "    Running initial format..."
      system("uv run ruff format . --quiet")
    end

    if options[:git]
      puts "    Initializing Git..."
      system("git init -q")
      File.write(".gitignore", ".ruff_cache\n.mypy_cache\n", mode: "a")
      system("git add .")
      system("git commit -q -m 'Init'")
    end
  else
    puts "Skipping install."
  end
end

puts "\nDone! Now run:"
puts "  cd #{project_name}"

if scripts_choice
  puts "  uv run poe dev"
else
  puts "  uv run main.py"
end