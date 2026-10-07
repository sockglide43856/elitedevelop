// static/js/sw.js

self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();

        const options = {
            body: data.body,
            icon: data.icon,
            badge: data.icon,
            data: {
                url: data.url // Where to go when notification is clicked
            }
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    // Open the app to the specific chat room URL
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});