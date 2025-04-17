const loggedInUserId = window.currentUserId;
const apiPrefix = window.apiPrefix;
const activeTab = window.activeTab;

let apiBaseUrl = "";
if (apiPrefix && apiPrefix !== "None") {
    apiBaseUrl = `/${apiPrefix}`;
}
