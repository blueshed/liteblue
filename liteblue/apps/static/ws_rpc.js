var protocol = document.location.protocol == "https:" ? "wss://" : "ws://";
var ws_url = protocol + document.domain + ":" + document.location.port;

class RpcClient {
    constructor(store, path) {
        this.store = store
        this._url = ws_url + path
        this._promises = []
        this._buffer = []
        this.connect()
    }
    connect() {
        this.store.commit("set_status", "ws connecting")
        var ws = new WebSocket(this._url)
        ws.onopen = () => {
            this.store.commit("set_status", "connected")
            if (this._buffer) {
                this._buffer.map((item) => {
                    this._ws.send(item)
                })
                this._buffer = null
            }
        }
        ws.onclose = () => {
            this.store.commit("set_status", "disconnected")
            location.reload(true)
        }
        ws.onmessage = (evt) => {
            let action = JSON.parse(evt.data)
            if (action['id']) {
                if (action.error) {
                    var error_obj = new Error(action.error.message)
                    error_obj.status_code = action.error.code
                    error_obj["original_payload"] = action.error
                    this._promises[action.id].reject(error_obj)
                } else {
                    this._promises[action.id].resolve(action.result)
                }
                delete this._promises[action.id]
            } else if (this.store._mutations[action.action]) {
                this.store.commit(action.action, action.message)
            } else {
                this.store.commit("set_broadcast", action)
            }
        }
        this._ws = ws
    }
    call(method, params) {
        return new Promise((resolve, reject) => {
            let _id = this.next_id()
            let msg = JSON.stringify({
                "jsonrpc": "2.0",
                "id": _id,
                "method": method,
                "params": params
            })
            if (this._buffer !== null) {
                this._buffer.push(msg)
            } else {
                this._ws.send(msg)
            }
            this._promises[_id] = {
                reject: reject,
                resolve: resolve
            }
        })
    }
    next_id() {
        return '_' + Math.random().toString(36).substr(2, 9);
    }
}

export default RpcClient