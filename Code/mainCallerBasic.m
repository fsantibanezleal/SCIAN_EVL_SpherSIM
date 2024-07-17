%% FASL 2013-2014
%  fsantibanezleal@ug.uchile.cl
%  fsantibanez@med.uchile.cl
%% Basic simulation enviroment for cell migration
%% Apporach oriented to DFCs migration -> KV embryogenesis
% Including layers for DFCS and EVL
%% Implementation on Spheric coordinates
% Agent based model for cellular migration
%% SemiDeformable model: Spheric nuclea plus gaussian noisy protusion 
% emulating filopodia

%%
%Main Callers

clear all
close all
clc

addpath('_Creation\');
addpath('_Draws\');
addpath('_GUIs\');
addpath('_Physics\');
addpath('_Geometric\');

%% Requiered Data for realistic simulation 

% Embryo Params
embryoData.embryo.radius = 1000;
% DFC paramas
embryoData.layerDFC.nDFCs = 24;
    % Mean radial size for initialize DFCs, in radians
    embryoData.layerDFC.radialSize  = pi/64;%((pi/2)/(nDFCs/2))/2;
    embryoData.layerDFC.nVertexsDFC = 20;
embryoData.layerDFC.minAzimuth      = -3*pi/4;%- pi/4;
embryoData.layerDFC.maxAzimuth      = embryoData.layerDFC.minAzimuth...
                                        + pi/4;
embryoData.layerDFC.maxElevation    =  pi/4;

    
% EVL params
embryoData.layerEVL.nVertexs = 10;
    % velocity per iteration for margin in spheric coordinates
    embryoData.layerEVL.marginVelocity.AER = [0,-(pi/2)*(1/200),0];


%% Create Enviroment 

enviroment = CreateEnviroment(embryoData);

%% Basic PLot functions
hMainSimFig = figure;
set(gcf, 'Position', get(0,'Screensize')); % Maximize figure.
rotate3d on
[xSphere,ySphere,zSphere] = sphere;
hSurface = ...
  surf(embryoData.embryo.radius.*xSphere,...
       embryoData.embryo.radius.*ySphere,...
       embryoData.embryo.radius.*zSphere); 
set(hSurface, 'FaceColor',[0 1 0], 'FaceAlpha',0.5, 'EdgeAlpha', 0);
%set(hSurface,'FaceColor',[0 1 0],'FaceAlpha',0.5);

DrawDFCLayer(enviroment.layerDFC,1);

%% Loop of migration
for dummyIndex = 1:100
    enviroment = UpdateLayers(enviroment);

    % Draw Section
    pause(0.01)
    hold off
    rotate3d on
    [xSphere,ySphere,zSphere] = sphere;
    hSurface = ...
      surf(embryoData.embryo.radius.*xSphere,...
           embryoData.embryo.radius.*ySphere,...
           embryoData.embryo.radius.*zSphere); 
    set(hSurface, 'FaceColor',[0 1 0], 'FaceAlpha',0.5, 'EdgeAlpha', 0);
    
    DrawDFCLayer(enviroment.layerDFC,1);
end



