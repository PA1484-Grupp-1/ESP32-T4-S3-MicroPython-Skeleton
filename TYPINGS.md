# How to add Typings to Visual Studio Code

1. Add a new file named `settings.json` under the `.vscode` folder
2. Add the following to that file
```json
{
    "python.analysis.stubPath": "./.typings"
}
```