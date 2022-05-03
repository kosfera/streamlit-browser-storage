
import {
    Streamlit,
    ComponentProps,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { useEffect } from "react"
import { CookieStorage } from "./CookieStorage";
import { LocalStorage } from "./LocalStorage";
import { SessionStorage } from "./SessionStorage";


let prevResult: string | null = null;
const BrowserStorage = (props: ComponentProps) => {

    const { args } = props

    const type = args["type"];
    const action = args["action"];
    const name = args["name"];
    const value = args["value"];
    const expires_at = args["expires_at"];

    let storage = new CookieStorage();
    switch (type) {
        case "LocalStorage":
            storage = new LocalStorage();
            break;

        case "SessionStorage":
            storage = new SessionStorage();
            break;
    }

    let result: any = null;
    switch (action) {
        case "SET":
            result = storage.set(name, value, expires_at);
            break;

        case "GET":
            result = storage.get(name) || "null|";
            break;

        case "GET_ALL":
            result = storage.getAll() || {};
            break;

        case "DELETE":
            result = storage.delete(name);
            break;

        default:
            break;
    }

    if (result && prevResult !== result) {
        result = JSON.stringify(result);
        prevResult = result;

        Streamlit.setComponentValue(result);
        Streamlit.setComponentReady();
    }

    useEffect(() => Streamlit.setFrameHeight());
    return <div></div>;
}

export default withStreamlitConnection(BrowserStorage);
