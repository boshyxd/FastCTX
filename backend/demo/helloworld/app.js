class Application {
    constructor(name) {
        this.name = name;
        this.modules = [];
    }

    addModule(module) {
        this.modules.push(module);
    }

    start() {
        console.log(`Starting ${this.name} application...`);
        this.modules.forEach(mod => mod.init());
    }
}

function createModule(name, initFunc) {
    return {
        name: name,
        init: initFunc
    };
}

const logger = createModule('Logger', () => {
    console.log('Logger initialized');
});

const database = createModule('Database', () => {
    console.log('Database connection established');
});

const app = new Application('HelloWorld');
app.addModule(logger);
app.addModule(database);
app.start();