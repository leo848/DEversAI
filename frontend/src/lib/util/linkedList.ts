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
		}
		if (this.next != null) {
			this.next.prev = this.next;
		} else {
			this.#list.popTail();
		}
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

	static fromIterable<T>(iter: Iterable<T>) {
		const list = new LinkedList();
		for (const item in iter) {
			list.append(item);
		}
		return list;
	}

	append(value: T) {
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

	prepend(value: T) {
		if (this.#size == 0) {
			this.append(value);
		}
		else {
			const newNode = new LinkedListNode(value, this);
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

	popTail() {
		this.#tail = this.#tail?.prev ?? null;
	}
}
