import * as vscode from 'vscode';

export class RustEmbeddedActionsProvider implements vscode.TreeDataProvider<ActionItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ActionItem | undefined | null | void> = new vscode.EventEmitter<ActionItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ActionItem | undefined | null | void> = this._onDidChangeTreeData.event;

    getTreeItem(element: ActionItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ActionItem): Thenable<ActionItem[]> {
        if (!element) {
            return Promise.resolve([
                new ActionItem(
                    '🏠 Panneau de Bienvenue',
                    'Ouvrir le panneau de bienvenue interactif',
                    vscode.TreeItemCollapsibleState.None,
                    'rustEmbedded.welcome'
                ),
                new ActionItem(
                    '📁 Nouveau Projet',
                    'Créer un nouveau projet Rust embarqué',
                    vscode.TreeItemCollapsibleState.None,
                    'rustEmbedded.createProject'
                ),
                new ActionItem(
                    '🛠️ Compiler',
                    'Compiler le projet actuel',
                    vscode.TreeItemCollapsibleState.None,
                    'rustEmbedded.buildProject'
                ),
                new ActionItem(
                    '⚡ Flasher',
                    'Flasher le firmware sur la carte',
                    vscode.TreeItemCollapsibleState.None,
                    'rustEmbedded.flashProject'
                ),
                new ActionItem(
                    '⚙️ Configuration',
                    'Configurer l\'environnement complet',
                    vscode.TreeItemCollapsibleState.None,
                    'rustEmbedded.setupEnvironment'
                )
            ]);
        }
        return Promise.resolve([]);
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
}

class ActionItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        tooltipText: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        commandId?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = tooltipText;
        
        if (commandId) {
            this.command = {
                command: commandId,
                title: label,
                arguments: []
            };
        }

        // Définir les icônes selon le label
        if (label.includes('🏠')) {
            this.iconPath = new vscode.ThemeIcon('home');
        } else if (label.includes('📁')) {
            this.iconPath = new vscode.ThemeIcon('add');
        } else if (label.includes('🛠️')) {
            this.iconPath = new vscode.ThemeIcon('tools');
        } else if (label.includes('⚡')) {
            this.iconPath = new vscode.ThemeIcon('rocket');
        } else if (label.includes('⚙️')) {
            this.iconPath = new vscode.ThemeIcon('gear');
        }
    }
}