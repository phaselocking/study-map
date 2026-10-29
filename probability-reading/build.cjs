// Render math at build time so the delivered page needs no JavaScript or network.
const fs = require('node:fs');
const path = require('node:path');
const args = process.argv.slice(2);
const argument = (name, fallback) => args.includes(name) ? args[args.indexOf(name)+1] : fallback;
const archive = path.resolve(argument('--archive', path.join(__dirname,'../probability-atlas')));
const output = path.resolve(argument('--output', path.join(__dirname,'index.html')));
const vendor = path.join(archive,'vendor/katex');
const katex = require(path.join(vendor,'katex.min.js'));
let template = fs.readFileSync(path.join(__dirname,'template.html'),'utf8');
let content = fs.readFileSync(path.join(__dirname,'content.html'),'utf8');
const images = {'CURVED_IMAGE':'cn-p16-curved-question.png','DEFINITION_IMAGE':'cn-p18-definition.png'};
for(const [key,filename] of Object.entries(images)){
  const data=fs.readFileSync(path.join(__dirname,'assets',filename));
  content=content.replaceAll('{{'+key+'}}','data:image/png;base64,'+data.toString('base64'));
}
let mathCount=0;
const decode = value => value.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
content = content.replace(/<math-tex(?: display="(block)")?>([\s\S]*?)<\/math-tex>/g,(_,block,tex)=>{
  mathCount++;
  const rendered=katex.renderToString(decode(tex),{displayMode:!!block,throwOnError:true,strict:'error',trust:false});
  return block?'<div class="math-block">'+rendered+'</div>':rendered;
});
let css=fs.readFileSync(path.join(vendor,'katex.min.css'),'utf8');
css=css.replace(/src:([^;]+)/g,(original,src)=>{
  const match=src.match(/url\(([^)]+\.woff2)\)/);
  if(!match)throw new Error('Expected WOFF2 source');
  const data=fs.readFileSync(path.join(vendor,match[1].replace(/["']/g,'')));
  return 'src:url(data:font/woff2;base64,'+data.toString('base64')+') format("woff2")';
});
const license=fs.readFileSync(path.join(vendor,'LICENSE'),'utf8').replace(/--/g,'—');
template=template.replace('{{CONTENT}}',content).replace('{{MATH_CSS}}','<style>'+css+'</style>').replace('{{MATH_JS}}','').replace('{{LICENSE}}',license);
if(/\{\{\w+\}\}|<math-tex|<script\b|(?:src|href)="(?:assets|vendor)\//i.test(template))throw new Error('Unresolved dependency or placeholder');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,template,'utf8');
process.stdout.write(JSON.stringify({output,bytes:Buffer.byteLength(template),formulas:mathCount,embeddedImages:Object.keys(images).length,scripts:0})+'\n');
