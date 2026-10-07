window.EliteFS = {

    data: null,

    async load() {

        const response = await fetch(
            window.ELITEOS_CONFIG.filesystemUrl,
            {
                credentials: "same-origin",
            }
        );

        const result = await response.json();

        if (!result.success) {
            throw new Error(
                result.error || "Could not load filesystem."
            );
        }

        this.data = result.filesystem;

        this.compressedSize =
            result.compressed_size;

        this.maxSize =
            result.max_size;

        return this.data;
    },


    get(path) {

        if (!this.data) {
            throw new Error(
                "Filesystem is not mounted."
            );
        }

        return this.data.files[path] || null;
    },


    exists(path) {

        return this.get(path) !== null;
    },


    read(path) {

        const file = this.get(path);

        if (!file) {
            throw new Error(
                `File not found: ${path}`
            );
        }

        if (file.type !== "file") {
            throw new Error(
                `${path} is not a file.`
            );
        }

        return file.content || "";
    },


    write(path, content) {

        if (!this.data) {
            throw new Error(
                "Filesystem is not mounted."
            );
        }

        this.data.files[path] = {
            type: "file",
            content: String(content),
        };
    },


    mkdir(path) {

        if (!this.data) {
            throw new Error(
                "Filesystem is not mounted."
            );
        }

        this.data.files[path] = {
            type: "directory",
        };
    },


    delete(path) {

        if (!this.exists(path)) {
            return;
        }

        delete this.data.files[path];
    },


    list(directory = "/") {

        const files = Object.entries(
            this.data.files
        );

        return files
            .filter(([path]) => {

                if (directory === "/") {

                    return path
                        .split("/")
                        .filter(Boolean)
                        .length === 1;
                }

                const normalized =
                    directory.endsWith("/")
                        ? directory
                        : directory + "/";

                const relative =
                    path.slice(normalized.length);

                return (
                    path.startsWith(normalized) &&
                    relative.length > 0 &&
                    !relative.includes("/")
                );
            })

            .map(([path, file]) => ({
                path,
                ...file,
            }));
    },


    async save() {

        const response = await fetch(

            window.ELITEOS_CONFIG.saveFilesystemUrl,

            {
                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type": "application/json",

                    "X-CSRFToken":
                        window.ELITEOS_CONFIG.csrfToken,
                },

                body: JSON.stringify({
                    filesystem: this.data,
                }),
            }
        );

        const result =
            await response.json();

        if (!response.ok) {

            const error =
                new Error(
                    result.error ||
                    "Filesystem could not be saved."
                );

            error.details = result;

            throw error;
        }

        this.compressedSize =
            result.compressed_size;

        this.maxSize =
            result.max_size;

        return result;
    },


    info() {

        return {

            format:
                this.data?.format,

            compressedSize:
                this.compressedSize,

            maxSize:
                this.maxSize,

            percent:
                this.maxSize
                    ? (
                        this.compressedSize /
                        this.maxSize
                    ) * 100
                    : 0,
        };
    },

};