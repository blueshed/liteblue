import WsClient from './ws_rpc.js';
import RpcClient from './es_rpc.js';

class Store {
    constructor() {
        this.status = null
        this.broadcast = null
        this.ping = null
        this._mutations = {
            set_status: (value) => {
                this.status = value
            },
            set_broadcast: (value) => {
                this.broadcast = value
            },
            ping: (value) => {
                this.ping = value
            }
        }
        this.$rpc = new WsClient(this, "/ws")
        // this.$rpc = new RpcClient(this, "/rpc", "/events")
    }
    output(data) {
        var parent = document.getElementById('output');
        var child = document.createElement("pre");
        child.innerHTML = JSON.stringify(data, null, 4);
        parent.insertBefore(child, parent.firstChild);
    }
    commit(action, value) {
        console.log(action, value)
        if (this._mutations[action]) {
            this._mutations[action](value)
        }
        if (value["action"] == "ping") return
        this.output(value)
    }
    dispatch(method, params) {
        return this.$rpc.call(method, params)
    }
}

function display_error(elem) {
    return (error) => {
        console.log(error);
        elem.innerHTML = `<div class='error'>${error}</div>`;
    }
}

function value_to_type(value, type) {
    if (type == "int") {
        value = parseInt(value)
    } else if (type == "float") {
        value = parseFloat(value)
    } else if (type == "bool") {
        let b = new Boolean(value);
        value = b.value_of();
    } else if (type == "dict") {
        value = JSON.parse(value);
    } else if (type == "list") {
        value = JSON.parse(value);
    }
    return value;
}

function add_panel(name, meta) {
    let panel = document.createElement('DIV');
    panel.className = "column box"
    let form = document.createElement('FORM');
    form.id = `${name}_form`
    let types = {};
    if (meta.params.length == 0) {
        form.innerHTML = `<div class="title">${name} - <input type="submit" name="submit" value="Send"></div>`;
    } else {
        form.innerHTML = `<div class="title">${name}</div>`;
        meta.params.map(param => {
            let name = param.trim();
            let type = ""
            let default_value = "";
            if (param.indexOf(":") != -1) {
                let values = param.split(":");
                name = values[0].trim();
                type = values[1].trim();
                if (type.indexOf("=") != -1) {
                    values = type.split("=")
                    type = values[0].trim();
                    default_value = values[1].trim();
                }
            } else if (param.indexOf("=") != -1) {
                let values = param.split("=");
                name = values[0].trim();
                default_value = values[1].trim();
            }
            let field = document.createElement("DIV");
            field.className = "field";
            if (type == 'list' || type == "dict") {
                field.innerHTML = `
<label>${name}:</label>
<textarea name="${name}" placeholder="${type} - json">${default_value}</textarea>
`
            } else {
                field.innerHTML = `
<label>${name}:</label>
<input type="text" name="${name}" value="${default_value}" placeholder="${type}">
`
            }
            form.appendChild(field);
            types[name] = {
                name: name,
                type: type,
                default_value: default_value
            }
        })
        let submit = document.createElement("DIV")
        submit.className = "field";
        submit.innerHTML = `
<label></label>
<input type="submit" name="submit" value="Send">
`
        form.appendChild(submit)
    }

    let result = document.createElement("DIV");
    result.className = "field result";
    let clear_btn = document.createElement('button');
    clear_btn.innerHTML = "clear";
    result.appendChild(clear_btn);
    clear_btn.style.display = "none";
    let label = document.createElement('label');
    label.innerHTML = "result:";
    result.appendChild(label);
    let pre = document.createElement("pre");
    pre.id = `${name}_result`;
    result.appendChild(pre);
    form.appendChild(result);

    clear_btn.addEventListener("click", (event) => {
        event.preventDefault();
        pre.innerHTML = "";
        clear_btn.style.display = "none";
        return false;
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        let params = {}
        let formData = new FormData(event.target);
        for (var pair of formData.entries()) {
            let type = types[pair[0]];
            params[pair[0]] = value_to_type(pair[1], type.type);
        }
        var result = document.getElementById(name + "_result");
        app.dispatch(name, params).then(function (response) {
            result.innerHTML = JSON.stringify(response, null, 2);
            clear_btn.style.display = "inline-block";
        }, display_error(result))
        return false;
    });

    panel.appendChild(form);
    return panel;
}

const app = new Store();

window.app = app;

app.dispatch("reflect", []).then(function (response) {
    let row = document.getElementsByClassName("row")[0];
    let procedures = response.procedures
    Object.keys(procedures).map(key => {
        let panel = add_panel(key, procedures[key]);
        row.appendChild(panel);
    })
});