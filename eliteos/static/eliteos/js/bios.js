window.EliteBIOS = {

    output: null,


    init() {

        this.output =
            document.getElementById(
                "bios-output"
            );
    },


    async print(message, delay = 120) {

        const line =
            document.createElement("div");

        line.textContent =
            message;

        this.output.appendChild(line);

        await new Promise(
            resolve =>
                setTimeout(
                    resolve,
                    delay
                )
        );
    },


    async boot() {

        this.init();

        this.output.innerHTML = "";

        await this.print(
            "Elite BIOS v1.0"
        );

        await this.print(
            "Initializing Elite Web Runtime..."
        );

        await this.print(
            "Mounting virtual filesystem..."
        );

        await EliteFS.load();

        await this.print(
            "Filesystem mounted."
        );

        await this.print(
            `Compressed image: ${EliteFS.compressedSize} bytes`
        );

        await this.print(
            `Filesystem limit: ${EliteFS.maxSize} bytes`
        );

        await this.print(
            "Searching for boot configuration..."
        );

        const biosConfig =
            EliteFS.read(
                "/boot/bios.json"
            );

        const config =
            JSON.parse(biosConfig);

        if (!config.boot) {

            throw new Error(
                "BIOS has no boot entry."
            );
        }

        await this.print(
            `Boot entry found: ${config.boot}`
        );

        await this.print(
            "Initializing EliteHTML runtime..."
        );

        await this.print(
            "BOOT OK"
        );

        return config;
    },

};