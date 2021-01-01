import process from 'process';

const isDev = !process.env.NODE_ENV || process.env.NODE_ENV === 'development';
export default isDev;
