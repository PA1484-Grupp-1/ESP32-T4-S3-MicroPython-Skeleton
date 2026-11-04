# How to add Typings/Autocomplete for LVGL to Visual Studio Code

1. Add a new file named `settings.json` under the `.vscode` folder
2. Add the following to that file
```json
{
    "python.analysis.stubPath": "./.typings"
}
```
3. To install additional stubs simply run the command in a new terminal (Top Left: Terminal > New Terminal) `pip install micropython-esp32-stubs`