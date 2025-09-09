import * as vscode from 'vscode';
import { RustEmbeddedProvider } from './rustEmbeddedProvider';
import { WelcomePanel } from './welcomePanel';
import { RustEmbeddedActionsProvider } from './actionsProvider';

export function activate(context: vscode.ExtensionContext) {
    const provider = new RustEmbeddedProvider(context);
    const actionsProvider = new RustEmbeddedActionsProvider();

    // Enregistrer le provider d'arbre pour la barre latérale
    vscode.window.registerTreeDataProvider('rustEmbeddedActions', actionsProvider);
    
    const disposables = [
        vscode.commands.registerCommand('rustEmbedded.welcome', () => {
            WelcomePanel.createOrShow(context.extensionUri, provider);
        }),
        vscode.commands.registerCommand('rustEmbedded.createProject', () => provider.createProject()),
        vscode.commands.registerCommand('rustEmbedded.buildProject', () => provider.buildProject()),
        vscode.commands.registerCommand('rustEmbedded.flashProject', () => provider.flashProject()),
        vscode.commands.registerCommand('rustEmbedded.installTarget', () => provider.installTarget()),
        vscode.commands.registerCommand('rustEmbedded.installTools', () => provider.installTools()),
        vscode.commands.registerCommand('rustEmbedded.setupEnvironment', () => provider.setupEnvironment())
    ];

    context.subscriptions.push(...disposables);

    // Afficher automatiquement le panneau de bienvenue au démarrage
    // seulement si aucun projet Rust n'est ouvert
    const hasCargoToml = vscode.workspace.findFiles('**/Cargo.toml', '**/node_modules/**', 1);
    hasCargoToml.then(files => {
        if (files.length === 0) {
            // Pas de Cargo.toml trouvé, montrer le panneau de bienvenue
            setTimeout(() => {
                WelcomePanel.createOrShow(context.extensionUri, provider);
            }, 1000);
        }
    });
}

export function deactivate() {}