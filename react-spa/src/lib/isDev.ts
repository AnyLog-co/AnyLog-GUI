import process from 'process';

const isDev = !process.env.NODE_ENV || ['development', 'test'].includes(process.env.NODE_ENV);
export default isDev;
