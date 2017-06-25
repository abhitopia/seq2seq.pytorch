#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import codecs
import torch
import torch.backends.cudnn as cudnn
from seq2seq.tools.inference import Translator
parser = argparse.ArgumentParser(
    description='Translate a file using pretrained model')

parser.add_argument('input', help='input file for translation')
parser.add_argument('-o', '--output', help='output file')
parser.add_argument('-m', '--model',
                    help='model checkpoint file')
parser.add_argument('--beam_size', default=12, type=int,
                    help='beam size used')
parser.add_argument('--max_sequence_length', default=100, type=int,
                    help='maximum prediciton length')
parser.add_argument('--length_normalization', default=0.6, type=float,
                    help='length normalization factor')
parser.add_argument('--devices', default='0',
                    help='device assignment (e.g "0,1", {"encoder":0, "decoder":1})')
parser.add_argument('--type', default='torch.cuda.FloatTensor',
                    help='type of tensor - e.g torch.cuda.HalfTensor')

if __name__ == '__main__':
    args = parser.parse_args()
    if 'cuda' in args.type:
        cuda = True
        main_gpu = 0
        if isinstance(args.devices, tuple):
            main_gpu = args.devices[0]
        elif isinstance(args.devices, int):
            main_gpu = args.devices
        elif isinstance(args.devices, dict):
            main_gpu = args.devices.get('input', 0)
        torch.cuda.set_device(main_gpu)
        cudnn.benchmark = True
    else:
        cuda = False
    checkpoint = torch.load(args.model)
    model = checkpoint['model']
    src_tok, target_tok = checkpoint['tokenizers'].values()
    translation_model = Translator(model,
                                   src_tok=src_tok,
                                   target_tok=target_tok,
                                   beam_size=args.beam_size,
                                   batch_first=model.batch_first,
                                   max_sequence_length=args.max_sequence_length,
                                   length_normalization_factor=args.length_normalization,
                                   cuda=cuda)

    output_file = codecs.open(args.output, 'w', encoding='UTF-8')
    with codecs.open(args.input, encoding='UTF-8') as input_file:
        for line in input_file:
            translated = translation_model.translate(line)
            output_file.write(translated)
            output_file.write('\n')
    output_file.close()
