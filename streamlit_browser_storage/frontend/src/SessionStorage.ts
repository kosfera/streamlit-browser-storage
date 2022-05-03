
import Cookies from "universal-cookie"


export class SessionStorage {
    cookies: Cookies;

    constructor() {
        this.cookies = new Cookies();
    }

    set(name: string, value: string, expires_at: string) {
        this.cookies.set(name, value, {
            path: "/",
            sameSite: "strict",
            expires: new Date(expires_at),
        });
        return true;
    }

    get(name: string): string {
        return this.cookies.get(name) || "null|";
    }

    getAll() {
        return this.cookies.getAll();
    }

    delete(name: string) {
        this.cookies.remove(name, { path: "/", sameSite: "strict" })
        return true
    }
}
