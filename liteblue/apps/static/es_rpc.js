/*
    Event Source as plugin to Vuex store
*/

function createEventSourcePlugin(url) {
    const source = new EventSource(url)
    return store => {
        store.commit("set_status", "es connecting")
        source.onopen = () => {
            store.commit("set_status", "connected")
        }
        source.onmessage = (message) => {
            let data = JSON.parse(message.data)
            if (store._mutations[message.action]) {
                store.commit(data.action, data.message)
            } else {
                store.commit("set_broadcast", data)
            }
        }
        source.onerror = () => {
            store.commit("set_status", "failed")
        }
    }
}

class RpcClient {
    constructor(store, path, events_path) {
        this.store = store
        this.path = path
        this._promises = []
        this._id = 1
        this._buffer = []
        createEventSourcePlugin(events_path)(this.store)
    }
    call(method, params) {
        this._id++
        return new Promise((resolve, reject) => {
            let msg = {
                "jsonrpc": "2.0",
                "id": this._id,
                "method": method,
                "params": params
            }
            axios.post(this.path, msg).then(
                response => {
                    let json = response.data
                    if (json.error) {
                        reject(json.error.message)
                    } else {
                        resolve(json.result)
                    }
                },
                error => {
                    reject(error)
                })
        })
    }
}

export default RpcClient