import type { Tuple } from './array';
import chroma from 'chroma-js';
import { leftPad } from './string';
import { assert } from './typed';

export class Color {
	static Category10 = [
		[0.12156862745098039, 0.4666666666666667, 0.7058823529411765],
		[1, 0.4980392156862745, 0.054901960784313725],
		[0.17254901960784313, 0.6274509803921569, 0.17254901960784313],
		[0.8392156862745098, 0.15294117647058825, 0.1568627450980392],
		[0.5803921568627451, 0.403921568627451, 0.7411764705882353],
		[0.5490196078431373, 0.33725490196078434, 0.29411764705882354],
		[0.8901960784313725, 0.4666666666666667, 0.7607843137254902],
		[0.4980392156862745, 0.4980392156862745, 0.4980392156862745],
		[0.7372549019607844, 0.7411764705882353, 0.13333333333333333],
		[0.09019607843137255, 0.7450980392156863, 0.8117647058823529]
	].map(([r, g, b]) => new Color(r, g, b));

	r: number;
	g: number;
	b: number;

	constructor(r: number, g: number, b: number) {
		this.r = r;
		this.g = g;
		this.b = b;
	}

	static luma(l: number): Color {
		return new Color(l, l, l);
	}

	chroma() {
		return chroma(this.toString());
	}

	readable() {
		return this.brightness() > 0.5 ? new Color(0, 0, 0) : new Color(1, 1, 1);
	}

	brightness() {
		return this.r * 0.2126 + this.g * 0.7152 + this.b * 0.0722;
	}

	saturate(f: number) {
		let chromaColor = this.chroma().saturate(f);
		return new Color(...(chromaColor.rgb().map((c: number) => c / 255) as Tuple<3, number>));
	}

	toString() {
		const { r, g, b } = this;
		const [ri, gi, bi] = [r, g, b].map((comp) => Math.floor(comp * 255));
		const n = ri * 256 * 256 + gi * 256 + bi;
		return '#' + leftPad(n.toString(16), '0', 6);
	}

	rgb(): Tuple<3, number> {
		const { r, g, b } = this;
		return [Math.floor(r * 255), Math.floor(g * 255), Math.floor(b * 255)];
	}

	lerp(other: Color, t: number): Color {
		return new Color(
			this.r + (other.r - this.r) * t,
			this.g + (other.g - this.g) * t,
			this.b + (other.b - this.b) * t
		);
	}
}

export class Gradient {
	static Viridis = new Gradient(
		[
			[3, 5, 26],
			[4, 5, 26],
			[5, 6, 27],
			[6, 7, 28],
			[7, 7, 29],
			[8, 8, 30],
			[10, 9, 31],
			[11, 9, 32],
			[13, 10, 33],
			[14, 11, 34],
			[16, 11, 35],
			[17, 12, 36],
			[19, 13, 37],
			[20, 14, 38],
			[22, 14, 39],
			[23, 15, 40],
			[24, 15, 41],
			[26, 16, 42],
			[27, 17, 43],
			[29, 17, 44],
			[30, 18, 45],
			[32, 18, 46],
			[33, 19, 48],
			[34, 19, 49],
			[36, 20, 50],
			[37, 20, 51],
			[39, 21, 52],
			[40, 21, 53],
			[42, 22, 54],
			[43, 22, 55],
			[45, 23, 56],
			[46, 23, 57],
			[48, 23, 58],
			[49, 24, 59],
			[51, 24, 60],
			[52, 25, 61],
			[53, 25, 62],
			[55, 25, 63],
			[56, 26, 64],
			[58, 26, 65],
			[60, 26, 66],
			[61, 26, 66],
			[63, 27, 67],
			[64, 27, 68],
			[66, 27, 69],
			[67, 28, 70],
			[69, 28, 71],
			[70, 28, 72],
			[72, 28, 72],
			[73, 29, 73],
			[75, 29, 74],
			[76, 29, 75],
			[78, 29, 75],
			[80, 29, 76],
			[81, 30, 77],
			[83, 30, 77],
			[84, 30, 78],
			[86, 30, 79],
			[88, 30, 79],
			[89, 30, 80],
			[91, 30, 81],
			[92, 30, 81],
			[94, 31, 82],
			[96, 31, 82],
			[97, 31, 83],
			[99, 31, 83],
			[100, 31, 84],
			[102, 31, 84],
			[104, 31, 85],
			[105, 31, 85],
			[107, 31, 86],
			[109, 31, 86],
			[110, 31, 87],
			[112, 31, 87],
			[113, 31, 87],
			[115, 31, 88],
			[117, 31, 88],
			[118, 31, 88],
			[120, 31, 89],
			[122, 31, 89],
			[123, 31, 89],
			[125, 31, 90],
			[127, 30, 90],
			[129, 30, 90],
			[130, 30, 90],
			[132, 30, 90],
			[134, 30, 91],
			[135, 30, 91],
			[137, 30, 91],
			[139, 29, 91],
			[140, 29, 91],
			[142, 29, 91],
			[144, 29, 91],
			[146, 28, 91],
			[147, 28, 91],
			[149, 28, 91],
			[151, 28, 91],
			[152, 27, 91],
			[154, 27, 91],
			[156, 27, 91],
			[158, 26, 91],
			[159, 26, 91],
			[161, 26, 91],
			[163, 25, 91],
			[164, 25, 91],
			[166, 25, 90],
			[168, 24, 90],
			[170, 24, 90],
			[171, 24, 90],
			[173, 23, 89],
			[175, 23, 89],
			[176, 23, 89],
			[178, 23, 88],
			[180, 22, 88],
			[181, 22, 87],
			[183, 22, 87],
			[185, 22, 87],
			[186, 22, 86],
			[188, 22, 86],
			[189, 22, 85],
			[191, 22, 84],
			[193, 23, 84],
			[194, 23, 83],
			[196, 23, 83],
			[197, 24, 82],
			[199, 25, 81],
			[200, 25, 81],
			[202, 26, 80],
			[203, 27, 79],
			[205, 28, 78],
			[206, 29, 78],
			[207, 30, 77],
			[209, 31, 76],
			[210, 32, 76],
			[211, 33, 75],
			[213, 34, 74],
			[214, 36, 73],
			[215, 37, 73],
			[216, 39, 72],
			[217, 40, 71],
			[219, 41, 70],
			[220, 43, 70],
			[221, 44, 69],
			[222, 46, 68],
			[223, 47, 68],
			[224, 49, 67],
			[225, 51, 66],
			[226, 52, 66],
			[227, 54, 65],
			[228, 56, 65],
			[229, 57, 64],
			[230, 59, 64],
			[231, 61, 63],
			[232, 63, 63],
			[232, 64, 62],
			[233, 66, 62],
			[234, 68, 62],
			[235, 70, 62],
			[235, 72, 62],
			[236, 74, 62],
			[236, 76, 62],
			[237, 78, 62],
			[237, 80, 62],
			[238, 82, 63],
			[238, 84, 63],
			[239, 86, 64],
			[239, 88, 64],
			[239, 90, 65],
			[240, 92, 66],
			[240, 94, 66],
			[240, 96, 67],
			[241, 98, 68],
			[241, 100, 69],
			[241, 102, 70],
			[242, 103, 71],
			[242, 105, 72],
			[242, 107, 73],
			[242, 109, 75],
			[242, 111, 76],
			[243, 113, 77],
			[243, 115, 78],
			[243, 116, 80],
			[243, 118, 81],
			[243, 120, 82],
			[244, 122, 84],
			[244, 124, 85],
			[244, 125, 87],
			[244, 127, 88],
			[244, 129, 90],
			[244, 131, 91],
			[244, 132, 93],
			[244, 134, 94],
			[245, 136, 96],
			[245, 138, 97],
			[245, 139, 99],
			[245, 141, 100],
			[245, 143, 102],
			[245, 144, 103],
			[245, 146, 105],
			[245, 148, 107],
			[245, 150, 108],
			[245, 151, 110],
			[245, 153, 112],
			[246, 155, 113],
			[246, 156, 115],
			[246, 158, 117],
			[246, 160, 119],
			[246, 161, 120],
			[246, 163, 122],
			[246, 164, 124],
			[246, 166, 126],
			[246, 168, 128],
			[246, 169, 129],
			[246, 171, 131],
			[246, 173, 133],
			[246, 174, 135],
			[246, 176, 137],
			[246, 177, 139],
			[246, 179, 141],
			[246, 180, 143],
			[246, 182, 145],
			[246, 184, 147],
			[246, 185, 149],
			[246, 187, 151],
			[246, 188, 153],
			[246, 190, 155],
			[246, 191, 157],
			[246, 193, 159],
			[247, 194, 162],
			[247, 196, 164],
			[247, 198, 166],
			[247, 199, 168],
			[247, 201, 170],
			[247, 202, 172],
			[247, 204, 175],
			[247, 205, 177],
			[247, 207, 179],
			[247, 208, 181],
			[248, 209, 184],
			[248, 211, 186],
			[248, 212, 188],
			[248, 214, 190],
			[248, 215, 192],
			[248, 217, 195],
			[248, 218, 197],
			[248, 220, 199],
			[249, 221, 201],
			[249, 223, 203],
			[249, 224, 205],
			[249, 226, 208],
			[249, 227, 210],
			[249, 229, 212],
			[250, 230, 214],
			[250, 232, 216],
			[250, 233, 218],
			[250, 235, 221]
		].map(([r, g, b]) => new Color(r / 256, g / 256, b / 256))
	);

	static Vlag = new Gradient(
		[
			[35, 105, 189],
			[38, 106, 189],
			[41, 108, 188],
			[44, 109, 188],
			[47, 110, 188],
			[49, 111, 188],
			[52, 112, 188],
			[54, 113, 188],
			[57, 114, 188],
			[59, 115, 188],
			[61, 116, 188],
			[63, 117, 188],
			[66, 118, 188],
			[68, 119, 188],
			[70, 120, 188],
			[72, 121, 188],
			[74, 123, 188],
			[76, 124, 188],
			[78, 125, 188],
			[80, 126, 188],
			[81, 127, 188],
			[83, 128, 188],
			[85, 129, 188],
			[87, 130, 188],
			[89, 131, 189],
			[91, 132, 189],
			[92, 133, 189],
			[94, 134, 189],
			[96, 135, 189],
			[98, 136, 189],
			[100, 137, 190],
			[101, 138, 190],
			[103, 139, 190],
			[105, 140, 190],
			[106, 141, 191],
			[108, 142, 191],
			[110, 144, 191],
			[111, 145, 191],
			[113, 146, 192],
			[115, 147, 192],
			[117, 148, 192],
			[118, 149, 193],
			[120, 150, 193],
			[121, 151, 193],
			[123, 152, 194],
			[125, 153, 194],
			[126, 154, 194],
			[128, 155, 195],
			[130, 156, 195],
			[131, 157, 196],
			[133, 158, 196],
			[135, 160, 196],
			[136, 161, 197],
			[138, 162, 197],
			[139, 163, 198],
			[141, 164, 198],
			[143, 165, 199],
			[144, 166, 199],
			[146, 167, 200],
			[147, 168, 200],
			[149, 169, 200],
			[151, 171, 201],
			[152, 172, 201],
			[154, 173, 202],
			[155, 174, 203],
			[157, 175, 203],
			[159, 176, 204],
			[160, 177, 204],
			[162, 178, 205],
			[163, 180, 205],
			[165, 181, 206],
			[167, 182, 206],
			[168, 183, 207],
			[170, 184, 208],
			[171, 185, 208],
			[173, 187, 209],
			[175, 188, 209],
			[176, 189, 210],
			[178, 190, 211],
			[179, 191, 211],
			[181, 192, 212],
			[183, 194, 213],
			[184, 195, 213],
			[186, 196, 214],
			[187, 197, 215],
			[189, 198, 215],
			[191, 200, 216],
			[192, 201, 217],
			[194, 202, 218],
			[195, 203, 218],
			[197, 205, 219],
			[199, 206, 220],
			[200, 207, 221],
			[202, 208, 221],
			[203, 209, 222],
			[205, 211, 223],
			[207, 212, 224],
			[208, 213, 224],
			[210, 215, 225],
			[212, 216, 226],
			[213, 217, 227],
			[215, 218, 228],
			[217, 220, 229],
			[218, 221, 229],
			[220, 222, 230],
			[221, 224, 231],
			[223, 225, 232],
			[225, 226, 233],
			[226, 227, 234],
			[228, 229, 235],
			[230, 230, 236],
			[231, 231, 236],
			[233, 233, 237],
			[235, 234, 238],
			[236, 235, 239],
			[238, 237, 240],
			[239, 238, 241],
			[241, 239, 242],
			[242, 240, 242],
			[243, 241, 243],
			[245, 242, 244],
			[246, 243, 244],
			[247, 244, 244],
			[248, 244, 245],
			[249, 245, 245],
			[249, 245, 245],
			[250, 245, 245],
			[250, 245, 245],
			[250, 245, 244],
			[250, 245, 244],
			[250, 244, 243],
			[250, 243, 243],
			[250, 243, 242],
			[250, 242, 241],
			[250, 240, 239],
			[249, 239, 238],
			[249, 238, 237],
			[248, 237, 235],
			[247, 235, 234],
			[247, 234, 232],
			[246, 232, 231],
			[245, 231, 229],
			[245, 229, 228],
			[244, 227, 226],
			[243, 226, 224],
			[242, 224, 223],
			[242, 223, 221],
			[241, 221, 219],
			[240, 219, 218],
			[239, 218, 216],
			[239, 216, 214],
			[238, 215, 213],
			[237, 213, 211],
			[236, 211, 210],
			[236, 210, 208],
			[235, 208, 206],
			[234, 207, 205],
			[234, 205, 203],
			[233, 203, 201],
			[232, 202, 200],
			[231, 200, 198],
			[231, 199, 197],
			[230, 197, 195],
			[229, 195, 193],
			[229, 194, 192],
			[228, 192, 190],
			[227, 191, 189],
			[227, 189, 187],
			[226, 188, 185],
			[225, 186, 184],
			[225, 185, 182],
			[224, 183, 181],
			[223, 181, 179],
			[223, 180, 178],
			[222, 178, 176],
			[222, 177, 174],
			[221, 175, 173],
			[220, 174, 171],
			[220, 172, 170],
			[219, 171, 168],
			[218, 169, 167],
			[218, 168, 165],
			[217, 166, 164],
			[217, 165, 162],
			[216, 163, 160],
			[215, 162, 159],
			[215, 160, 157],
			[214, 159, 156],
			[213, 157, 154],
			[213, 156, 153],
			[212, 154, 151],
			[212, 152, 150],
			[211, 151, 148],
			[210, 149, 147],
			[210, 148, 145],
			[209, 146, 144],
			[209, 145, 142],
			[208, 143, 141],
			[207, 142, 139],
			[207, 140, 138],
			[206, 139, 136],
			[205, 137, 135],
			[205, 136, 133],
			[204, 135, 132],
			[204, 133, 130],
			[203, 132, 129],
			[202, 130, 127],
			[202, 129, 126],
			[201, 127, 125],
			[200, 126, 123],
			[200, 124, 122],
			[199, 123, 120],
			[199, 121, 119],
			[198, 120, 117],
			[197, 118, 116],
			[197, 117, 114],
			[196, 115, 113],
			[195, 114, 111],
			[195, 112, 110],
			[194, 111, 109],
			[193, 109, 107],
			[193, 108, 106],
			[192, 106, 104],
			[192, 105, 103],
			[191, 103, 101],
			[190, 102, 100],
			[190, 100, 99],
			[189, 99, 97],
			[188, 97, 96],
			[188, 96, 94],
			[187, 94, 93],
			[186, 93, 92],
			[185, 91, 90],
			[185, 90, 89],
			[184, 88, 87],
			[183, 87, 86],
			[183, 85, 85],
			[182, 84, 83],
			[181, 82, 82],
			[181, 81, 81],
			[180, 79, 79],
			[179, 77, 78],
			[178, 76, 76],
			[178, 74, 75],
			[177, 73, 74],
			[176, 71, 72],
			[175, 70, 71],
			[175, 68, 70],
			[174, 66, 68],
			[173, 65, 67],
			[172, 63, 66],
			[172, 62, 64],
			[171, 60, 63],
			[170, 58, 62],
			[169, 57, 60],
			[169, 55, 59]
		].map(([r, g, b]) => new Color(r / 256, g / 256, b / 256))
	);

	stops: Color[];

	constructor(stops: Color[]) {
		this.stops = stops;
	}

	sample(t: number) {
		assert(!Number.isNaN(t), 'value is nan');
		t = Math.min(1, Math.max(t, 0));
		const leftIndex = Math.floor((this.stops.length - 2) * t);
		const rightIndex = Math.floor((this.stops.length - 2) * t + 1);
		const [leftColor, rightColor] = [leftIndex, rightIndex].map((index) => this.stops[index]);
		const leftWeight = t % (1 / this.stops.length);
		const rightWeight = 1 - leftWeight;
		return new Color(
			leftColor.r * leftWeight + rightColor.r * rightWeight,
			leftColor.g * leftWeight + rightColor.g * rightWeight,
			leftColor.b * leftWeight + rightColor.b * rightWeight
		);
	}

	reverse() {
		return new Gradient(this.stops.slice().reverse());
	}

	css(direction: string = 'to right'): string {
		let string = `linear-gradient(${direction}, `;
		string += this.stops.join(', ');
		string += ')';
		return string;
	}
}
