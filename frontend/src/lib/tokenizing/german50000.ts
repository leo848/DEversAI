import { Vocabulary } from '$lib/tokenizing/vocabulary';
import raw from './german50000.base64.txt?raw';

export default Vocabulary.fromBase64(raw);
