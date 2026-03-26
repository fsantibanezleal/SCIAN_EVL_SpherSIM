/**
 * WebSocket client for SpherSIM real-time simulation streaming.
 *
 * Manages the connection lifecycle (connect, reconnect, close) and
 * dispatches incoming simulation state to registered callbacks.
 */

class SimWebSocket {
    /**
     * @param {string} url  - WebSocket endpoint URL.
     * @param {function} onMessage - Callback receiving parsed JSON state.
     * @param {function} onStatusChange - Callback receiving status string.
     */
    constructor(url, onMessage, onStatusChange) {
        this.url = url;
        this.onMessage = onMessage;
        this.onStatusChange = onStatusChange || (() => {});
        this.ws = null;
        this.reconnectDelay = 2000;
        this._reconnectTimer = null;
    }

    /** Open the WebSocket connection. */
    connect() {
        if (this.ws && this.ws.readyState <= WebSocket.OPEN) {
            return;
        }

        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            this.onStatusChange('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.onMessage(data);
            } catch (err) {
                console.error('WebSocket parse error:', err);
            }
        };

        this.ws.onclose = () => {
            this.onStatusChange('disconnected');
            this._scheduleReconnect();
        };

        this.ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            this.onStatusChange('error');
        };
    }

    /** Send a JSON command to the server. */
    send(obj) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(obj));
        }
    }

    /** Close the connection and cancel any pending reconnect. */
    close() {
        clearTimeout(this._reconnectTimer);
        if (this.ws) {
            this.ws.onclose = null;
            this.ws.close();
            this.ws = null;
        }
        this.onStatusChange('disconnected');
    }

    /** @private Schedule an automatic reconnect attempt. */
    _scheduleReconnect() {
        clearTimeout(this._reconnectTimer);
        this._reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);
    }
}
