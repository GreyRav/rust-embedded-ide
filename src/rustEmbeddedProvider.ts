import { spawn } from 'child_process';
import * as vscode from 'vscode';
import * as path from 'path';

export class RustEmbeddedProvider {
    private context: vscode.ExtensionContext;
    private pythonCommand: string | null = null;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    private getWorkspaceFolder(): string | undefined {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage("Veuillez ouvrir un dossier de projet.");
            return undefined;
        }
        return workspaceFolder;
    }

    private getPythonCommand(): string {
        // Cache la détection pour éviter de la répéter
        if (this.pythonCommand) {
            return this.pythonCommand;
        }

        // Détection automatique de la commande Python disponible
        const { execSync } = require('child_process');
        
        try {
            // Test python3 en premier (plus courant sur Linux/macOS)
            execSync('python3 --version', { stdio: 'ignore' });
            this.pythonCommand = 'python3';
            return 'python3';
        } catch {
            try {
                // Fallback vers python (Windows/certains systèmes)
                execSync('python --version', { stdio: 'ignore' });
                this.pythonCommand = 'python';
                return 'python';
            } catch {
                // Aucun Python trouvé
                throw new Error('Python n\'est pas installé ou non disponible dans PATH');
            }
        }
    }

    private runPythonScript(action: string, target?: string, projectName?: string): void {
        const workspaceFolder = this.getWorkspaceFolder();
        if (!workspaceFolder) return;

        const scriptPath = path.join(this.context.extensionPath, 'main.py');
        
        const terminal = vscode.window.createTerminal(`Rust Embedded - ${action}`);
        terminal.show();

        try {
            const pythonCmd = this.getPythonCommand();
            let command = `${pythonCmd} "${scriptPath}" ${action} --project-path "${workspaceFolder}"`;
            
            if (target) {
                command += ` --target ${target}`;
            }
            
            if (projectName) {
                command += ` --project-name ${projectName}`;
            }
            
            // Afficher quelle commande Python est utilisée
            terminal.sendText(`echo "🐍 Utilisation de: ${pythonCmd}"`);
            terminal.sendText(command);
        } catch (error) {
            vscode.window.showErrorMessage(
                `Erreur: ${error}. Veuillez installer Python 3.x et l'ajouter au PATH.`
            );
        }
    }

    async createProject(): Promise<void> {
        // Demander le nom du projet
        const projectName = await vscode.window.showInputBox({
            prompt: 'Nom du projet Rust embarqué',
            placeHolder: 'mon-projet-embarque',
            validateInput: (value) => {
                if (!value || value.trim() === '') {
                    return 'Le nom du projet ne peut pas être vide';
                }
                if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
                    return 'Le nom du projet ne peut contenir que des lettres, chiffres, tirets et underscores';
                }
                return null;
            }
        });

        if (!projectName) return;

        // Demander la target
        const targetOptions = [
            { label: 'Raspberry Pi Pico (RP2040)', target: 'pico' },
            { label: 'ESP32-C3', target: 'esp32c3' }
        ];

        const selectedTarget = await vscode.window.showQuickPick(targetOptions, {
            placeHolder: 'Sélectionnez votre carte cible'
        });

        if (!selectedTarget) return;

        await this.createProjectWithTarget(selectedTarget.target, projectName);
    }

    async createProjectWithTarget(target: string, projectName?: string): Promise<void> {
        if (!projectName) {
            projectName = await vscode.window.showInputBox({
                prompt: `Nom du projet pour ${target === 'pico' ? 'Raspberry Pi Pico' : 'ESP32-C3'}`,
                placeHolder: `mon-projet-${target}`,
                validateInput: (value) => {
                    if (!value || value.trim() === '') {
                        return 'Le nom du projet ne peut pas être vide';
                    }
                    if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
                        return 'Le nom du projet ne peut contenir que des lettres, chiffres, tirets et underscores';
                    }
                    return null;
                }
            });
        }

        if (!projectName) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Création du projet ${projectName}...`,
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            this.runPythonScript('create', target, projectName);
            
            // Attendre un peu puis proposer d'ouvrir le nouveau projet
            setTimeout(async () => {
                const workspaceFolder = this.getWorkspaceFolder();
                if (workspaceFolder) {
                    const projectPath = path.join(workspaceFolder, projectName!);
                    const openProject = await vscode.window.showInformationMessage(
                        `Projet ${projectName} créé avec succès!`,
                        'Ouvrir le projet'
                    );
                    
                    if (openProject === 'Ouvrir le projet') {
                        const uri = vscode.Uri.file(projectPath);
                        await vscode.commands.executeCommand('vscode.openFolder', uri);
                    }
                }
            }, 2000);
        });
    }

    async buildProject(): Promise<void> {
        const target = await this.selectTarget();
        if (!target) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Compilation pour ${target}...`,
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            this.runPythonScript('build', target);
        });
    }

    async flashProject(): Promise<void> {
        const target = await this.selectTarget();
        if (!target) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Flashage pour ${target}...`,
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            this.runPythonScript('flash', target);
        });
    }

    async installTarget(): Promise<void> {
        const targetOptions = [
            { label: 'Toutes les targets', target: undefined },
            { label: 'Raspberry Pi Pico (thumbv6m-none-eabi)', target: 'pico' },
            { label: 'ESP32-C3 (riscv32imc-unknown-none-elf)', target: 'esp32c3' }
        ];

        const selectedTarget = await vscode.window.showQuickPick(targetOptions, {
            placeHolder: 'Sélectionnez les targets Rust à installer'
        });

        if (selectedTarget === undefined) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Installation des targets Rust...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            this.runPythonScript('install-target', selectedTarget.target);
        });
    }

    async installTools(): Promise<void> {
        const toolOptions = [
            { label: 'Tous les outils', target: undefined },
            { label: 'probe-rs (pour Pico)', target: 'pico' },
            { label: 'espflash (pour ESP32-C3)', target: 'esp32c3' }
        ];

        const selectedTool = await vscode.window.showQuickPick(toolOptions, {
            placeHolder: 'Sélectionnez les outils à installer'
        });

        if (selectedTool === undefined) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Installation des outils de flashage...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            this.runPythonScript('install-tools', selectedTool.target);
        });
    }

    async setupEnvironment(): Promise<void> {
        // Vérifier d'abord que Python est disponible
        try {
            const pythonCmd = this.getPythonCommand();
            const { execSync } = require('child_process');
            const version = execSync(`${pythonCmd} --version`, { encoding: 'utf8' }).trim();
            
            const confirm = await vscode.window.showInformationMessage(
                `Configuration avec ${version}. Installer toutes les targets Rust et outils nécessaires ?`,
                'Oui', 'Non'
            );

            if (confirm !== 'Oui') return;

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Configuration de l\'environnement de développement...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                this.runPythonScript('setup');
            });
        } catch (error) {
            vscode.window.showErrorMessage(
                `Erreur: ${error}. Veuillez installer Python 3.x et l'ajouter au PATH.`
            );
        }
    }

    private async selectTarget(): Promise<string | undefined> {
        const targetOptions = [
            { label: 'Raspberry Pi Pico (RP2040)', target: 'pico' },
            { label: 'ESP32-C3', target: 'esp32c3' }
        ];

        const selectedTarget = await vscode.window.showQuickPick(targetOptions, {
            placeHolder: 'Sélectionnez votre carte cible'
        });

        return selectedTarget?.target;
    }
}