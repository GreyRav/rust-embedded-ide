import * as vscode from 'vscode';
import { RustEmbeddedProvider } from './rustEmbeddedProvider';

export class WelcomePanel {
    public static currentPanel: WelcomePanel | undefined;
    public static readonly viewType = 'rustEmbeddedWelcome';
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private provider: RustEmbeddedProvider;

    public static createOrShow(extensionUri: vscode.Uri, provider: RustEmbeddedProvider) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (WelcomePanel.currentPanel) {
            WelcomePanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            WelcomePanel.viewType,
            'Rust Embedded - Bienvenue',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'images'),
                ]
            }
        );

        WelcomePanel.currentPanel = new WelcomePanel(panel, extensionUri, provider);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, provider: RustEmbeddedProvider) {
        this._panel = panel;
        this.provider = provider;

        this._update();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'createProject':
                        await this.provider.createProjectWithTarget(message.target);
                        return;
                    case 'setupEnvironment':
                        await this.provider.setupEnvironment();
                        return;
                    case 'openExistingProject':
                        await vscode.commands.executeCommand('vscode.openFolder');
                        return;
                }
            },
            null,
            this._disposables
        );
    }

    public dispose() {
        WelcomePanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rust Embedded - Bienvenue</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    padding: 20px;
                    background: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    margin: 0;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                }
                
                .logo {
                    font-size: 48px;
                    font-weight: bold;
                    color: #ff6b35;
                    margin-bottom: 10px;
                }
                
                .subtitle {
                    font-size: 18px;
                    color: var(--vscode-descriptionForeground);
                    margin-bottom: 30px;
                }
                
                .cards-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .card {
                    background: var(--vscode-input-background);
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 8px;
                    padding: 20px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-align: center;
                }
                
                .card:hover {
                    background: var(--vscode-list-hoverBackground);
                    border-color: var(--vscode-focusBorder);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                
                .card-icon {
                    font-size: 48px;
                    margin-bottom: 15px;
                    display: block;
                }
                
                .pico { color: #e91e63; }
                .esp32 { color: #2196f3; }
                .setup { color: #4caf50; }
                .open { color: #ff9800; }
                
                .card-title {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: var(--vscode-editor-foreground);
                }
                
                .card-description {
                    font-size: 14px;
                    color: var(--vscode-descriptionForeground);
                    line-height: 1.4;
                }
                
                .features {
                    background: var(--vscode-textBlockQuote-background);
                    border-left: 4px solid #ff6b35;
                    padding: 20px;
                    margin-top: 30px;
                    border-radius: 4px;
                }
                
                .features h3 {
                    margin-top: 0;
                    color: #ff6b35;
                }
                
                .features ul {
                    margin: 0;
                    padding-left: 20px;
                }
                
                .features li {
                    margin-bottom: 8px;
                    color: var(--vscode-editor-foreground);
                }
                
                .quick-actions {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 30px;
                    flex-wrap: wrap;
                }
                
                .action-btn {
                    padding: 12px 24px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: background-color 0.2s ease;
                }
                
                .action-btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                
                .action-btn.secondary {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }
                
                .action-btn.secondary:hover {
                    background: var(--vscode-button-secondaryHoverBackground);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">[#] Rust Embedded</div>
                <div class="subtitle">Developpement embarque pour ESP32-C3 et Raspberry Pi Pico</div>
            </div>
            
            <div class="cards-container">
                <div class="card" onclick="createProject('pico')">
                    <span class="card-icon pico">🍓</span>
                    <div class="card-title">Raspberry Pi Pico</div>
                    <div class="card-description">
                        Creer un nouveau projet pour RP2040<br>
                        <strong>Target:</strong> thumbv6m-none-eabi<br>
                        <strong>Flasher:</strong> probe-rs
                    </div>
                </div>
                
                <div class="card" onclick="createProject('esp32c3')">
                    <span class="card-icon esp32">📡</span>
                    <div class="card-title">ESP32-C3</div>
                    <div class="card-description">
                        Creer un nouveau projet pour ESP32-C3<br>
                        <strong>Target:</strong> riscv32imc-unknown-none-elf<br>
                        <strong>Flasher:</strong> espflash
                    </div>
                </div>
                
                <div class="card" onclick="setupEnvironment()">
                    <span class="card-icon setup">⚙️</span>
                    <div class="card-title">Configurer l'Environnement</div>
                    <div class="card-description">
                        <strong>⚠️ Recommande avant le premier usage</strong><br>
                        Installer toutes les targets Rust<br>
                        et les outils de flashage<br>
                        (probe-rs-tools, espflash)
                    </div>
                </div>
                
                <div class="card" onclick="openExistingProject()">
                    <span class="card-icon open">📁</span>
                    <div class="card-title">Ouvrir un Projet</div>
                    <div class="card-description">
                        Ouvrir un projet Rust<br>
                        embarque existant<br>
                        dans VS Code
                    </div>
                </div>
            </div>
            
            <div class="features">
                <h3>🚀 Fonctionnalites</h3>
                <ul>
                    <li>Templates preconfigures pour ESP32-C3 et Pico RP2040</li>
                    <li>Compilation automatisee avec les bonnes targets</li>
                    <li>Flashage direct depuis VS Code</li>
                    <li>Configuration automatique des environnements</li>
                    <li>Support des HAL specifiques a chaque carte</li>
                </ul>
            </div>
            
            <div class="quick-actions">
                <button class="action-btn" onclick="vscode.postMessage({command: 'setupEnvironment'})">
                    🔧 Configuration Complete
                </button>
                <button class="action-btn secondary" onclick="openDocumentation()">
                    📚 Documentation
                </button>
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                
                function createProject(target) {
                    vscode.postMessage({
                        command: 'createProject',
                        target: target
                    });
                }
                
                function setupEnvironment() {
                    vscode.postMessage({
                        command: 'setupEnvironment'
                    });
                }
                
                function openExistingProject() {
                    vscode.postMessage({
                        command: 'openExistingProject'
                    });
                }
                
                function openDocumentation() {
                    // Ouvrir la documentation dans le navigateur
                    vscode.postMessage({
                        command: 'openDocumentation'
                    });
                }
            </script>
        </body>
        </html>`;
    }
}