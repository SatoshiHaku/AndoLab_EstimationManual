const { ipcRenderer } = require('electron')
const { spawn } = require('child_process')

function sendToPyCurveFit(dir) {
	return new Promise((resolve, reject) => {
		let python = spawn('python', [`${__dirname}/../stfmr.py`, "curve", dir]);
		python.stdout.on('data', function (data) {
			console.log("Python response: ", data.toString('utf8'));
		});

		python.stderr.on('data', (data) => {
			console.error(`stderr: ${data}`);
		});

		python.on('close', (code) => {
			console.log(`child process exited with code ${code}`);
			if (code == 0) {
				resolve();
			} else {
				reject();
			}
		});
	})
}

function sendToPyKittelLineFit(dir, theta, df, dn) {
	return new Promise((resolve, reject) => {
		let python = spawn('python', [`${__dirname}/../stfmr.py`, "kittelline", dir, theta, df, dn]);
		python.stdout.on('data', function (data) {
			console.log("Python response: ", data.toString('utf8'));
		});

		python.stderr.on('data', (data) => {
			console.error(`stderr: ${data}`);
		});

		python.on('close', (code) => {
			console.log(`child process exited with code ${code}`);
			if (code == 0) {
				resolve();
			} else {
				reject();
			}
		});
	})
}


function Button2OpenFolder() {
	ipcRenderer.send('render2main_open_dir')
}

function Button2TriggerFitCurve() {

	// curve fitting preparation
	let dirList = []
	let checkbox = data.querySelectorAll('input[type="checkbox"]');
	checkbox.forEach(eachBox => {
		if (eachBox.checked) {
			dir = eachBox.value
			dirList.push(dir)
		}
	});
	console.log(dirList);

	// Kittel & line fitting preparation
	let kittelParaList = [];
	let theta = document.getElementById("input_theta").value;
	checkbox.forEach(eachBox => {
		if (eachBox.checked) {
			let dir = eachBox.value;
			let df = document.getElementById(`input_${dir}/df`).value;
			let dn = document.getElementById(`input_${dir}/dn`).value;
			kittelParaList.push([dir, df, dn]);
		}
	});
	Promise.all(dirList.map((dir) => {
		return sendToPyCurveFit(dir);
	})).then(() => {
		Promise.all(kittelParaList.map((para) => {
			return sendToPyKittelLineFit(para[0], theta, para[1], para[2]);
		}));
	}).catch();
}

const fs = require('fs')
ipcRenderer.on('open_dir', (event, arg) => {
	data.innerHTML = ""
	data.insertAdjacentHTML('beforeend', `<a href="javascript:Button2TriggerFitCurve();">Fit Curve...</a>`)
	let path = String(arg[0])
	console.log(path);
	const allDirents = fs.readdirSync(path, { withFileTypes: true });
	const dirNames = allDirents.filter(dirent => dirent.isDirectory()).map(({ name }) => name);
	let table = document.createElement('table');

	//Magnetic Field angle
	let tr = document.createElement('tr');
	let td = document.createElement('td');
	td.textContent = "Magnetic Field angle (deg):"
	tr.appendChild(td);

	td = document.createElement('td');
	let inputBox = document.createElement("input");
	inputBox.setAttribute("type", "text");
	inputBox.setAttribute("class", "input_box");
	inputBox.setAttribute("id", "input_theta");
	td.appendChild(inputBox);
	tr.appendChild(td);
	table.appendChild(tr);

	// Directory Name
	tr = document.createElement('tr');
	td = document.createElement('th');
	td.textContent = "Dir";
	tr.appendChild(td);

	// df input
	td = document.createElement('th');
	td.textContent = "df"
	tr.appendChild(td);

	// dn input
	td = document.createElement('th');
	td.textContent = "dn"
	tr.appendChild(td);

	// checkbox to select whether to include the data or not
	td = document.createElement('th');
	td.textContent = "include data"
	tr.appendChild(td);
	table.appendChild(tr);

	for (const dir of dirNames) {
		// Directory Name
		let tr = document.createElement('tr');
		let td = document.createElement('td');
		td.textContent = dir;
		tr.appendChild(td);

		// df input
		let inputBox = document.createElement("input");
		inputBox.setAttribute("type", "text");
		inputBox.setAttribute("class", "input_box");
		inputBox.setAttribute("id", `input_${path}/${dir}/df`);
		td = document.createElement('td');
		td.appendChild(inputBox);
		tr.appendChild(td);

		// dn input
		inputBox = document.createElement("input");
		inputBox.setAttribute("type", "text");
		inputBox.setAttribute("class", "input_box");
		inputBox.setAttribute("id", `input_${path}/${dir}/dn`);
		td = document.createElement('td');
		td.appendChild(inputBox);
		tr.appendChild(td);

		// checkbox
		inputBox = document.createElement("input");
		inputBox.setAttribute("type", "checkbox");
		inputBox.setAttribute("value", `${path}/${dir}`);
		inputBox.setAttribute('checked', 'checked');;
		td = document.createElement('td');
		td.appendChild(inputBox);
		tr.appendChild(td);

		table.appendChild(tr);
	}
	document.getElementById('data').appendChild(table);
});


