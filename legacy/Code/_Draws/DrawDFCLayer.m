function y = DrawDFCLayer(layerDFC,vHold)

    numDFCs = size(layerDFC.cellDFC,2);
    if ~vHold
        figure;
    end
    
    for indexDFC = 1:numDFCs
        hold on;            
        plot3(...
            layerDFC.cellDFC(indexDFC).contour.XYZ(:,1),...
            layerDFC.cellDFC(indexDFC).contour.XYZ(:,2),...
            layerDFC.cellDFC(indexDFC).contour.XYZ(:,3))

        hold on;

        plot3(...
            layerDFC.cellDFC(indexDFC).contour.XYZ([1 end],1),...
            layerDFC.cellDFC(indexDFC).contour.XYZ([1 end]:2,2),...
            layerDFC.cellDFC(indexDFC).contour.XYZ([1 end]:2,3))
    end
    dimAxis = 2000;
    axis([-dimAxis dimAxis -dimAxis dimAxis -dimAxis dimAxis])
end