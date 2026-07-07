type LogLevel = 'INFO' | 'WARN' | 'ERROR'

const styles: Record<LogLevel, string> = {
  INFO: 'color:#00F0FF',
  WARN: 'color:#FBBF24',
  ERROR: 'color:#FB7185'
}

/** Unified logger: `[NebulaScreen][LEVEL][timestamp] message`. */
export class Logger {
  private static write(level: LogLevel, message: unknown, ...rest: unknown[]): void {
    const ts = new Date().toISOString()
    const prefix = `[NebulaScreen][${level}][${ts}]`
    const method = level === 'ERROR' ? 'error' : level === 'WARN' ? 'warn' : 'log'
    // eslint-disable-next-line no-console
    console[method](`%c${prefix}`, styles[level], message, ...rest)
  }

  static info(message: unknown, ...rest: unknown[]): void {
    Logger.write('INFO', message, ...rest)
  }

  static warn(message: unknown, ...rest: unknown[]): void {
    Logger.write('WARN', message, ...rest)
  }

  static error(message: unknown, ...rest: unknown[]): void {
    Logger.write('ERROR', message, ...rest)
  }
}
