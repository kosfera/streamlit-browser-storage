
import {
    Streamlit,
    ComponentProps,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { useEffect } from "react"
import { CookieStorage } from "./CookieStorage";
import { LocalStorage } from "./LocalStorage";
import { SessionStorage } from "./SessionStorage";
import _ from "underscore";

let prevResults: any = {};
const BrowserStorage = (props: ComponentProps) => {

    const { args } = props

    const type = args["type"];
    const action = args["action"];
    const name = args["name"];
    const value = args["value"];
    const expiresAt = args["expires_at"];

    let storage: any = new CookieStorage();
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
            result = storage.set(name, value, expiresAt);
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

    if (result && !_.isEqual(prevResults[action], result)) {
        prevResults[action] = result;

        Streamlit.setComponentValue(JSON.stringify(result));
        Streamlit.setComponentReady();
    }

    useEffect(() => Streamlit.setFrameHeight(0));
    return <div></div>;
}

export default withStreamlitConnection(BrowserStorage);
