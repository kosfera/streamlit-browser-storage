
import _ from "underscore";

export class LocalStorage {

    storage = localStorage;

    set(name: string, value: string, expires_at: string) {
        this.storage.setItem(name, value);
        return true;
    }

    get(name: string): string {
        this.deleteExpired();
        return this.storage.getItem(name) || "null|";
    }

    getAll() {
        this.deleteExpired();

        let all: any = {};
        Object.keys(this.storage).forEach(name => {
            let value = this.storage.getItem(name);

            all[name] = value;
        });
        return all;
    }

    delete(name: string) {
        this.storage.removeItem(name);
        return true
    }

    deleteExpired() {
        let now = Date.now();

        Object.keys(this.storage).forEach(name => {
            let value = this.storage.getItem(name);

            if (!_.isNull(value)) {
                let m = /\|(\d+|)$/.exec(value);

                if (!_.isNull(m) && m[1].length > 0) {
                    let expiresAt = 1000 * parseInt(m[1]);

                    if (now >= expiresAt) {
                        this.delete(name);
                    }
                }
            }
        });
    }
}
