const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const exec = require('child_process').exec;

let mainWindow;

function createWindow() {
	mainWindow = new BrowserWindow({
		webPreferences: {
			nodeIntegration: true,
		},
		width: 800,
		height: 600,
		useContentSize: true,
	});

	mainWindow.loadURL(`file://${__dirname}/index.html`);

	mainWindow.webContents.openDevTools();
}
function createMenu() {
	const template = [
		{
			label: 'File',
			submenu: [
				{
					label: 'Open Folder..',
					accelerator: 'CmdOrCtrl+O', // ショートカットキーを設定
					click: () => { openDir() } // 実行される関数
				}
			]
		},
		{
			label: 'Help',
			submenu: [
				{
					label: 'about'
				},
				{
					label: 'Quit',
					accelerator: 'CmdOrCtrl+Q',
					click: () => { app.quit(); }
				}
			]
		}
	]
	const menu = Menu.buildFromTemplate(template)
	Menu.setApplicationMenu(menu);
}

function openDir() {
	let folderPath = dialog.showOpenDialogSync(null, {
		properties: ['openDirectory'],
		title: 'Select a folder',
		defaultPath: '.',
	});
	mainWindow.webContents.send('open_dir', folderPath);
}

app.on('ready', () => {
	createWindow();
	createMenu();
});

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit();
	}
});
app.on('activate', () => {
	if (mainWindow === null) {
		createWindow();
	}
});

ipcMain.on('render2main_open_dir', (event, arg) => {
	openDir()
})
