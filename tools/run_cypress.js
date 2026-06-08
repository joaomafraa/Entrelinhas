const http = require('http');
const { spawn, spawnSync } = require('child_process');

const mode = process.argv.includes('--open') ? 'open' : 'run';
const slow = process.argv.includes('--slow');
const specIndex = process.argv.indexOf('--spec');
const spec = specIndex >= 0 ? process.argv[specIndex + 1] : null;
const python = process.env.PYTHON || 'python';
const port = process.env.CYPRESS_DJANGO_PORT || '8000';
const host = '127.0.0.1';
const baseUrl = `http://${host}:${port}`;

const env = {
  ...process.env,
  SECRET_KEY: process.env.SECRET_KEY || 'django-insecure-cypress-test-key',
  DEBUG: process.env.DEBUG || 'True',
  ALLOWED_HOSTS: process.env.ALLOWED_HOSTS || '127.0.0.1,localhost,testserver',
  CSRF_TRUSTED_ORIGINS: process.env.CSRF_TRUSTED_ORIGINS || 'http://localhost',
};
const cypressEnv = { ...env };

delete cypressEnv.ELECTRON_RUN_AS_NODE;

function waitForServer(url, isServerRunning, attempts = 40) {
  return new Promise((resolve, reject) => {
    let currentAttempt = 0;

    function check() {
      if (!isServerRunning()) {
        reject(new Error('Django server stopped before it became ready.'));
        return;
      }

      currentAttempt += 1;

      const request = http.get(url, (response) => {
        response.resume();
        resolve();
      });

      request.on('error', () => {
        if (currentAttempt >= attempts) {
          reject(new Error(`Django server did not respond at ${url}`));
          return;
        }

        setTimeout(check, 1000);
      });

      request.setTimeout(2000, () => {
        request.destroy();
      });
    }

    check();
  });
}

function runCommand(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: 'inherit',
    env,
    ...options,
  });

  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

async function main() {
  console.log('Applying Django migrations...');
  runCommand(python, ['manage.py', 'migrate', '--noinput']);

  console.log('Collecting static files...');
  runCommand(python, ['manage.py', 'collectstatic', '--noinput']);

  console.log(`Starting Django server at ${baseUrl}...`);
  const server = spawn(
    python,
    ['manage.py', 'runserver', `${host}:${port}`, '--noreload'],
    {
      stdio: 'inherit',
      env,
    }
  );

  const stopServer = () => {
    if (process.platform === 'win32' && server.pid) {
      spawnSync('taskkill', ['/PID', String(server.pid), '/T', '/F'], {
        stdio: 'ignore',
      });
      return;
    }

    if (!server.killed) {
      server.kill();
    }
  };

  process.on('exit', stopServer);
  process.on('SIGINT', () => {
    stopServer();
    process.exit(130);
  });
  process.on('SIGTERM', () => {
    stopServer();
    process.exit(143);
  });

  try {
    await waitForServer(`${baseUrl}/`, () => server.exitCode === null);
    console.log('Django server is ready.');

    const cypressArgs = [mode, '--config', `baseUrl=${baseUrl}`];

    if (slow) {
      cypressArgs.push('--env', 'screencast=true,stepDelay=1800,typeDelay=55');
    }

    if (spec) {
      cypressArgs.push('--spec', spec);
    }

    console.log(`Running Cypress in ${mode} mode...`);
    runCommand(process.execPath, ['node_modules/cypress/bin/cypress', ...cypressArgs], {
      env: cypressEnv,
    });
  } finally {
    stopServer();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
