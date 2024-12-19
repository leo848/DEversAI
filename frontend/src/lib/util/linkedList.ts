export class LinkedListNode<T> {
	value: T;

	next: LinkedListNode<T> | null;
	prev: LinkedListNode<T> | null;

	#list: LinkedList<T>;

	constructor(value: T, list: LinkedList<T>) {
		this.value = value;
		this.#list = list;
		this.next = null;
		this.prev = null;
	}

	remove() {
		if (this.prev != null) {
			this.prev.next = this.next;
		} else {
			this.#list.popHead();
		}

		if (this.next != null) {
			this.next.prev = this.prev;
		} else {
			this.#list.popTail();
		}
		this.prev = null;
		this.next = null;
	}
}

export class LinkedList<T> {
	#head: LinkedListNode<T> | null = null;
	#tail: LinkedListNode<T> | null = null;
	#size: number

	constructor() {
		this.#size = 0
		this.#head = null
		this.#tail = null
	}

	static fromIterable<T>(iter: Iterable<T>): LinkedList<T> {
		const list = new LinkedList<T>();
		for (const item of iter) {
			list.append(item);
		}
		return list;
	}

	forEach(f: (value: T) => void) {
		for (let listNode = this.head(); listNode != null; listNode = listNode.next) {
			f(listNode.value);
		}
	}

	prepend(value: T) {
		const newNode = new LinkedListNode(value, this);
		if (this.#size == 0) {
			this.#head = newNode;
			this.#tail = newNode;
		} else {
			this.#head!.prev = newNode;
			newNode.next = this.#head;
			this.#head = newNode;
		}
		this.#size += 1;
	}

	append(value: T) {
		const newNode = new LinkedListNode(value, this);
		if (this.#size == 0) {
			this.#head = newNode;
			this.#tail = newNode;
		} else {
			this.#tail!.next = newNode;
			newNode.prev = this.#tail;
			this.#tail = newNode;
		}
		this.#size += 1;
	}

	head() {
		return this.#head;
	}

	tail() {
		return this.#tail;
	}

	popHead() {
		this.#head = this.#head?.next ?? null;
		if (this.#head != null) {
			this.#head!.prev = null;
		}
	}

	popTail() {
		this.#tail = this.#tail?.prev ?? null;
		if (this.#tail != null) {
			this.#tail!.next = null;
		}
	}

	size() {
		return this.#size;
	}

	toArray(): T[] {
		const array = [];
		let currentNode = this.head();
		while (currentNode != null) {
			array.push(currentNode.value);
			currentNode = currentNode.next;
		}
		return array;
	}
}
