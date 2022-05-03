
import Cookies from "universal-cookie"


export class CookieStorage {
    cookies: Cookies;

    constructor() {
        this.cookies = new Cookies();
    }

    set(name: string, value: string, expires_at: string) {

        let extra: any = {};
        if (expires_at) {
            extra["expires"] = new Date(expires_at);
        }

        this.cookies.set(name, value, {
            path: "/",
            sameSite: "strict",
            ...extra,
        });
        return true;
    }

    get(name: string): string {
        return this.cookies.get(name);
    }

    getAll() {
        return this.cookies.getAll({ doNotParse: true });
    }

    delete(name: string) {
        this.cookies.remove(name, { path: "/", sameSite: "strict" })
        return true
    }
}
