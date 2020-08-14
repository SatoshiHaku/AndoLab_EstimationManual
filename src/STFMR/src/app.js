const { ipcRenderer } = require('electron');
ipcRenderer.on('open_dir', (event, arg) => {
	ipcRenderer.send('open_dir_ret', arg);
});
